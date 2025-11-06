"""Regressive proof engine for nominative determinism claims.

This module reconstructs observed asset performance from linguistic drivers,
enabling falsifiable, back-tested validation of the platform's theory.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from core.models import (
    db,
    Cryptocurrency,
    Domain,
    DomainAnalysis,
    Hurricane,
    HurricaneAnalysis,
    MTGCard,
    MTGCardAnalysis,
    NameAnalysis,
    PriceHistory,
)

logger = logging.getLogger(__name__)


@dataclass
class RegressiveClaim:
    """Configuration for a regressively-proven hypothesis."""

    claim_id: str
    asset_type: str  # 'crypto' or 'domain'
    target_column: str
    target_kind: str = "continuous"  # 'continuous' or 'binary'
    description: str = ""
    features: List[str] = field(default_factory=list)
    control_features: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    sample_floor: int = 60
    breakout_threshold: Optional[float] = None
    notes: Optional[str] = None

    def all_features(self) -> List[str]:
        return list(dict.fromkeys(self.features + self.control_features))


class RegressiveProofEngine:
    """Runs regressive analyses that back-solve performance from name features."""

    def __init__(self, cv_folds: int = 5):
        self.cv_folds = cv_folds
        self.base_output_dir = Path(__file__).resolve().parents[1] / "analysis_outputs" / "regressive_proof"
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_claim(
        self,
        claim: Union[RegressiveClaim, Dict[str, Any]],
        persist: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Execute a regressive analysis for the provided claim."""

        claim_obj = self._normalize_claim(claim)
        logger.info("Regressive proof: running claim %s", claim_obj.claim_id)

        dataset = self._load_dataset(claim_obj)
        if dataset.empty:
            logger.warning("Claim %s dataset empty", claim_obj.claim_id)
            result = self._empty_result(claim_obj, "no_data")
            if persist:
                self._persist_result(result, output_dir)
            return result

        dataset = self._apply_filters(dataset, claim_obj.filters)
        missing_cols = [col for col in claim_obj.all_features() + [claim_obj.target_column] if col not in dataset.columns]
        if missing_cols:
            message = f"Missing required columns: {missing_cols}"
            logger.error("Claim %s %s", claim_obj.claim_id, message)
            result = self._empty_result(claim_obj, "missing_columns", warnings=[message])
            if persist:
                self._persist_result(result, output_dir)
            return result

        working_df = dataset[claim_obj.all_features() + [claim_obj.target_column]].dropna()
        sample_size = len(working_df)

        if sample_size < claim_obj.sample_floor:
            warning = (
                f"Sample size {sample_size} below floor {claim_obj.sample_floor} for claim {claim_obj.claim_id}"
            )
            logger.warning(warning)
            result = self._empty_result(claim_obj, "insufficient_sample", warnings=[warning], sample_size=sample_size)
            if persist:
                self._persist_result(result, output_dir)
            return result

        X = working_df[claim_obj.all_features()].astype(float)
        y = working_df[claim_obj.target_column]

        if claim_obj.target_kind == "binary":
            y = y.astype(int)
            sm_model, sm_metrics = self._fit_logistic(X, y)
            cv_metrics = self._cross_validate_classifier(X, y)
        else:
            y = y.astype(float)
            sm_model, sm_metrics = self._fit_linear(X, y)
            cv_metrics = self._cross_validate_regressor(X, y)

        effect_insights = self._derive_effects(claim_obj, working_df)

        result = {
            "claim": asdict(claim_obj),
            "status": "ok",
            "sample_size": sample_size,
            "model_summary": {
                **sm_metrics,
                "cross_validation": cv_metrics,
            },
            "coefficients": self._extract_coefficients(sm_model),
            "effect_analysis": effect_insights,
            "warnings": sm_metrics.get("warnings", []),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if persist:
            self._persist_result(result, output_dir)

        return result

    # ------------------------------------------------------------------
    # Dataset assembly
    # ------------------------------------------------------------------
    def _load_dataset(self, claim: RegressiveClaim) -> pd.DataFrame:
        if claim.asset_type == "crypto":
            return self._get_crypto_dataframe(claim)
        if claim.asset_type == "domain":
            return self._get_domain_dataframe()
        if claim.asset_type == "hurricane":
            return self._get_hurricane_dataframe()
        if claim.asset_type == "mtg":
            return self._get_mtg_dataframe()
        raise ValueError(f"Unsupported asset_type: {claim.asset_type}")

    def _get_crypto_dataframe(self, claim: RegressiveClaim) -> pd.DataFrame:
        latest_prices_subq = (
            db.session.query(
                PriceHistory.crypto_id,
                db.func.max(PriceHistory.date).label("max_date"),
            )
            .group_by(PriceHistory.crypto_id)
            .subquery()
        )

        query = (
            db.session.query(Cryptocurrency, NameAnalysis, PriceHistory)
            .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)
            .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)
            .join(
                latest_prices_subq,
                db.and_(
                    PriceHistory.crypto_id == latest_prices_subq.c.crypto_id,
                    PriceHistory.date == latest_prices_subq.c.max_date,
                ),
            )
        )

        rows: List[Dict[str, Any]] = []
        breakout_threshold = claim.breakout_threshold or 100

        for crypto, analysis, price in query.all():
            if not analysis:
                continue

            # Parse category tags safely
            tags: List[str] = []
            if analysis.category_tags:
                try:
                    raw = json.loads(analysis.category_tags)
                    if isinstance(raw, list):
                        tags = [str(t).lower() for t in raw]
                except (json.JSONDecodeError, TypeError):
                    tags = []

            semantic = (analysis.semantic_category or "").lower()
            tech_signals = {"tech", "technology", "ai", "data", "network", "compute", "quant"}
            tech_tag = int(
                any(term in semantic for term in tech_signals)
                or any(term in tag for tag in tags for term in tech_signals)
            )

            market_cap = crypto.market_cap or 0
            total_volume = crypto.total_volume or 0

            return_1yr = price.price_1yr_change
            breakout_flag = (
                1
                if return_1yr is not None and breakout_threshold is not None and return_1yr >= breakout_threshold
                else 0
            )

            row = {
                "asset_id": crypto.id,
                "asset_name": crypto.name,
                "symbol": crypto.symbol,
                "rank": crypto.rank,
                "log_rank": np.log1p(crypto.rank) if crypto.rank else None,
                "market_cap": market_cap,
                "log_market_cap": np.log1p(market_cap) if market_cap > 0 else None,
                "total_volume": total_volume,
                "log_total_volume": np.log1p(total_volume) if total_volume > 0 else None,
                "volume_to_cap": (total_volume / market_cap) if market_cap else None,
                "return_30d": price.price_30d_change,
                "return_90d": price.price_90d_change,
                "return_1yr": return_1yr,
                "normalized_return_1yr": None,
                "return_ath": price.price_ath_change,
                "is_breakout_flag": breakout_flag,
                "is_breakout_100": 1 if return_1yr is not None and return_1yr >= 100 else 0,
                "syllable_count": analysis.syllable_count,
                "character_length": analysis.character_length,
                "word_count": analysis.word_count,
                "phonetic_score": analysis.phonetic_score,
                "vowel_ratio": analysis.vowel_ratio,
                "memorability_score": analysis.memorability_score,
                "pronounceability_score": analysis.pronounceability_score,
                "uniqueness_score": analysis.uniqueness_score,
                "name_type_percentile": analysis.name_type_percentile,
                "is_optimal_syllable": int(analysis.syllable_count in (2, 3))
                if analysis.syllable_count is not None
                else None,
                "tech_tag": tech_tag,
                "is_active": int(bool(crypto.is_active)),
            }

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if df["return_1yr"].notna().sum() > 1:
            mean_val = df["return_1yr"].mean()
            std_val = df["return_1yr"].std(ddof=0)
            if std_val and not math.isclose(std_val, 0.0):
                df["normalized_return_1yr"] = (df["return_1yr"] - mean_val) / std_val

        return df

    def _get_domain_dataframe(self) -> pd.DataFrame:
        query = db.session.query(Domain, DomainAnalysis).join(
            DomainAnalysis, Domain.id == DomainAnalysis.domain_id
        )

        rows: List[Dict[str, Any]] = []
        for domain, analysis in query.all():
            sale_price = domain.sale_price or 0
            char_length = analysis.character_length

            row = {
                "domain_id": domain.id,
                "full_domain": domain.full_domain,
                "tld": domain.tld.lower() if domain.tld else None,
                "sale_price": domain.sale_price,
                "log_sale_price": math.log(sale_price) if sale_price > 0 else None,
                "sale_year": domain.sale_date.year if domain.sale_date else None,
                "brandability_score": domain.brandability_score,
                "keyword_score": domain.keyword_score,
                "tld_premium_multiplier": domain.tld_premium_multiplier,
                "days_on_market": domain.days_on_market,
                "auction_failed": int(domain.auction_failed) if domain.auction_failed is not None else None,
                "syllable_count": analysis.syllable_count,
                "character_length": char_length,
                "phonetic_score": analysis.phonetic_score,
                "memorability_score": analysis.memorability_score,
                "pronounceability_score": analysis.pronounceability_score,
                "uniqueness_score": analysis.uniqueness_score,
                "is_optimal_syllable": int(analysis.syllable_count in (2, 3))
                if analysis.syllable_count is not None
                else None,
                "is_ultra_short": int(char_length is not None and char_length <= 3),
                "tld_is_ai": int(domain.tld.lower() == "ai") if domain.tld else None,
                "tld_is_com": int(domain.tld.lower() == "com") if domain.tld else None,
                "tld_is_io": int(domain.tld.lower() == "io") if domain.tld else None,
            }

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        return df

    def _get_hurricane_dataframe(self) -> pd.DataFrame:
        """Assemble hurricane dataset with name features and outcome variables."""
        query = db.session.query(Hurricane, HurricaneAnalysis).join(
            HurricaneAnalysis, Hurricane.id == HurricaneAnalysis.hurricane_id
        )

        rows: List[Dict[str, Any]] = []
        for hurricane, analysis in query.all():
            deaths = hurricane.deaths or 0
            damage = hurricane.damage_usd or 0
            
            # Create gender dummy variables
            gender_male = int(analysis.gender_coded == 'male') if analysis.gender_coded else 0
            gender_female = int(analysis.gender_coded == 'female') if analysis.gender_coded else 0
            
            # Log-transform outcomes for better regression properties
            log_deaths = math.log1p(deaths) if deaths >= 0 else None
            log_damage = math.log(damage) if damage > 0 else None
            
            # Create decade bins for time controls
            decade = (hurricane.year // 10) * 10 if hurricane.year else None
            
            # Calculate derived outcome variables for new claims
            deaths_direct = hurricane.deaths_direct or 0
            deaths_indirect = hurricane.deaths_indirect or 0
            evac_ordered = hurricane.evacuations_ordered or 0
            evac_actual = hurricane.evacuations_actual or 0
            
            # Avoidable death ratio (indirect/direct) - higher = worse post-storm behavior
            avoidable_death_ratio = (deaths_indirect / deaths_direct) if deaths_direct > 0 else None
            
            # Evacuation compliance rate (actual/ordered) - higher = better compliance
            evacuation_compliance_rate = (evac_actual / evac_ordered) if evac_ordered > 0 else None
            
            row = {
                "hurricane_id": hurricane.id,
                "storm_name": hurricane.name,
                "year": hurricane.year,
                "decade": decade,
                "basin": hurricane.basin,
                "saffir_simpson_category": hurricane.saffir_simpson_category or 0,
                "max_wind_mph": hurricane.max_wind_mph,
                "min_pressure_mb": hurricane.min_pressure_mb,
                "landfall_state": hurricane.landfall_state,
                "deaths": deaths,
                "deaths_direct": deaths_direct,
                "deaths_indirect": deaths_indirect,
                "log_deaths": log_deaths,
                "injuries": hurricane.injuries,
                "damage_usd": damage,
                "log_damage_usd": log_damage,
                "fema_aid_usd": hurricane.fema_aid_usd,
                "news_mention_count": hurricane.news_mention_count,
                # New outcome metrics
                "avoidable_death_ratio": avoidable_death_ratio,
                "evacuation_compliance_rate": evacuation_compliance_rate,
                "evacuations_ordered": evac_ordered,
                "evacuations_actual": evac_actual,
                "displaced_persons": hurricane.displaced_persons,
                "shelters_opened": hurricane.shelters_opened,
                "media_mentions_prelandfall": hurricane.media_mentions_prelandfall,
                "media_mentions_postlandfall": hurricane.media_mentions_postlandfall,
                "coastal_population_exposed": hurricane.coastal_population_exposed,
                "prior_hurricanes_5yr": hurricane.prior_hurricanes_5yr,
                # Name features
                "syllable_count": analysis.syllable_count,
                "character_length": analysis.character_length,
                "phonetic_score": analysis.phonetic_score,
                "vowel_ratio": analysis.vowel_ratio,
                "memorability_score": analysis.memorability_score,
                "pronounceability_score": analysis.pronounceability_score,
                "uniqueness_score": analysis.uniqueness_score,
                "phonetic_harshness_score": analysis.phonetic_harshness_score,
                "gender_coded": analysis.gender_coded,
                "gender_male": gender_male,
                "gender_female": gender_female,
                "sentiment_polarity": analysis.sentiment_polarity,
                "alphabetical_position": analysis.alphabetical_position,
                # Binary outcomes
                "is_major_hurricane": int(hurricane.saffir_simpson_category >= 3) if hurricane.saffir_simpson_category else 0,
                "has_casualties": int(deaths > 0),
                "has_major_damage": int(damage > 1000000) if damage else 0,
            }

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)

    def _get_mtg_dataframe(self) -> pd.DataFrame:
        """Assemble MTG card dataset with name features and market value."""
        query = db.session.query(MTGCard, MTGCardAnalysis).join(
            MTGCardAnalysis, MTGCard.id == MTGCardAnalysis.card_id
        )

        rows: List[Dict[str, Any]] = []
        for card, analysis in query.all():
            price_usd = card.price_usd or 0
            
            # Create card type dummies
            type_line = (card.card_type or '').lower()
            is_instant = int('instant' in type_line and 'sorcery' not in type_line)
            is_sorcery = int('sorcery' in type_line)
            is_enchantment = int('enchantment' in type_line)
            is_artifact = int('artifact' in type_line and 'creature' not in type_line)
            is_planeswalker = int('planeswalker' in type_line)
            
            # Price bins for classification
            is_valuable = int(price_usd > 5.0) if price_usd else 0
            is_premium = int(price_usd > 20.0) if price_usd else 0
            
            # CMC bins
            cmc = card.converted_mana_cost or 0
            cmc_low = int(cmc <= 2)
            cmc_mid = int(3 <= cmc <= 5)
            cmc_high = int(cmc >= 6)
            
            row = {
                "card_id": card.id,
                "card_name": card.name,
                "set_code": card.set_code,
                "rarity": card.rarity,
                "rarity_tier": card.rarity_tier,
                "is_mythic": int(card.rarity == 'mythic'),
                "is_rare": int(card.rarity == 'rare'),
                "converted_mana_cost": cmc,
                "cmc_low": cmc_low,
                "cmc_mid": cmc_mid,
                "cmc_high": cmc_high,
                "is_legendary": int(card.is_legendary),
                "is_creature": int(card.is_creature),
                "is_instant": is_instant,
                "is_sorcery": is_sorcery,
                "is_instant_sorcery": int(card.is_instant_sorcery),
                "is_enchantment": is_enchantment,
                "is_artifact": is_artifact,
                "is_planeswalker": is_planeswalker,
                "color_identity": card.color_identity,
                "price_usd": price_usd,
                "log_price_usd": card.log_price_usd,
                "price_usd_foil": card.price_usd_foil,
                "edhrec_rank": card.edhrec_rank,
                "log_edhrec_rank": math.log1p(card.edhrec_rank) if card.edhrec_rank else None,
                "num_decks": card.num_decks,
                "is_valuable": is_valuable,
                "is_premium": is_premium,
                "release_year": card.release_date.year if card.release_date else None,
                "syllable_count": analysis.syllable_count,
                "character_length": analysis.character_length,
                "word_count": analysis.word_count,
                "phonetic_score": analysis.phonetic_score,
                "vowel_ratio": analysis.vowel_ratio,
                "memorability_score": analysis.memorability_score,
                "pronounceability_score": analysis.pronounceability_score,
                "uniqueness_score": analysis.uniqueness_score,
                "fantasy_score": analysis.fantasy_score,
                "power_connotation_score": analysis.power_connotation_score,
                "mythic_resonance_score": analysis.mythic_resonance_score,
                "flavor_text_sentiment": analysis.flavor_text_sentiment,
                "constructed_language_score": analysis.constructed_language_score,
            }

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Modeling helpers
    # ------------------------------------------------------------------
    def _fit_linear(self, X: pd.DataFrame, y: pd.Series):
        X_sm = sm.add_constant(X)
        try:
            model = sm.OLS(y, X_sm).fit()
            metrics = {
                "model_type": "OLS",
                "primary_metric": "r_squared",
                "r_squared": float(model.rsquared),
                "adj_r_squared": float(model.rsquared_adj),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "rmse": float(math.sqrt(model.mse_resid)) if model.mse_resid is not None else None,
            }
            return model, metrics
        except Exception as exc:  # pragma: no cover - defensive
            warning = f"OLS fit failed: {exc}"
            logger.error(warning)
            return None, {"model_type": "OLS", "primary_metric": "r_squared", "warnings": [warning]}

    def _fit_logistic(self, X: pd.DataFrame, y: pd.Series):
        X_sm = sm.add_constant(X)
        try:
            model = sm.Logit(y, X_sm).fit(disp=False, maxiter=1000)
            preds = (model.predict(X_sm) >= 0.5).astype(int)
            accuracy = float((preds == y).mean())
            metrics = {
                "model_type": "Logit",
                "primary_metric": "pseudo_r_squared",
                "pseudo_r_squared": float(model.prsquared),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "log_likelihood": float(model.llf),
                "accuracy": accuracy,
            }
            return model, metrics
        except (sm.tools.sm_exceptions.PerfectSeparationError, np.linalg.LinAlgError) as exc:
            warning = f"Logistic regression failed: {exc}"
            logger.error(warning)
            return None, {"model_type": "Logit", "primary_metric": "pseudo_r_squared", "warnings": [warning]}

    def _cross_validate_classifier(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        if y.nunique() < 2:
            return {
                "metric": "roc_auc",
                "folds": 0,
                "scores": [],
                "mean_score": None,
                "std_score": None,
                "warnings": ["Only one class present"],
            }

        folds = min(self.cv_folds, len(X))
        if folds < 2:
            return {
                "metric": "roc_auc",
                "folds": 0,
                "scores": [],
                "mean_score": None,
                "std_score": None,
                "warnings": ["Insufficient samples for cross-validation"],
            }

        estimator = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
            ]
        )

        kf = KFold(n_splits=folds, shuffle=True, random_state=42)
        try:
            roc_scores = cross_val_score(estimator, X, y, cv=kf, scoring="roc_auc")
            acc_scores = cross_val_score(estimator, X, y, cv=kf, scoring="accuracy")
            return {
                "metric": "roc_auc",
                "folds": folds,
                "scores": [float(s) for s in roc_scores],
                "mean_score": float(np.mean(roc_scores)),
                "std_score": float(np.std(roc_scores)),
                "auxiliary": {
                    "accuracy_mean": float(np.mean(acc_scores)),
                    "accuracy_std": float(np.std(acc_scores)),
                },
            }
        except ValueError as exc:
            warning = f"Classifier CV failed: {exc}"
            logger.error(warning)
            return {
                "metric": "roc_auc",
                "folds": folds,
                "scores": [],
                "mean_score": None,
                "std_score": None,
                "warnings": [warning],
            }

    def _cross_validate_regressor(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        folds = min(self.cv_folds, len(X))
        if folds < 2:
            return {
                "metric": "r2",
                "folds": 0,
                "scores": [],
                "mean_score": None,
                "std_score": None,
                "warnings": ["Insufficient samples for cross-validation"],
            }

        estimator = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("reg", Ridge(alpha=1.0)),
            ]
        )

        kf = KFold(n_splits=folds, shuffle=True, random_state=42)
        try:
            r2_scores = cross_val_score(estimator, X, y, cv=kf, scoring="r2")
            rmse_scores = cross_val_score(estimator, X, y, cv=kf, scoring="neg_root_mean_squared_error")
            return {
                "metric": "r2",
                "folds": folds,
                "scores": [float(s) for s in r2_scores],
                "mean_score": float(np.mean(r2_scores)),
                "std_score": float(np.std(r2_scores)),
                "auxiliary": {
                    "rmse_mean": float(np.mean(-rmse_scores)),
                    "rmse_std": float(np.std(-rmse_scores)),
                },
            }
        except ValueError as exc:
            warning = f"Regressor CV failed: {exc}"
            logger.error(warning)
            return {
                "metric": "r2",
                "folds": folds,
                "scores": [],
                "mean_score": None,
                "std_score": None,
                "warnings": [warning],
            }

    def _derive_effects(self, claim: RegressiveClaim, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}

        if claim.target_kind == "binary":
            groups = df.groupby(claim.target_column)
            if set(groups.groups.keys()) >= {0, 1}:
                positive = groups.get_group(1)
                negative = groups.get_group(0)
                positive_mean = {
                    col: float(positive[col].mean())
                    for col in claim.features
                    if col in positive.columns
                }
                negative_mean = {
                    col: float(negative[col].mean())
                    for col in claim.features
                    if col in negative.columns
                }
                lift = {
                    col: positive_mean[col] - negative_mean.get(col, 0.0)
                    for col in positive_mean
                }
                return {
                    "group_sizes": {
                        "positive": int(len(positive)),
                        "negative": int(len(negative)),
                    },
                    "positive_mean": positive_mean,
                    "negative_mean": negative_mean,
                    "lift": lift,
                    "positive_share": float(len(positive) / len(df)),
                }
            return {"warnings": ["Binary effect analysis requires both classes"]}

        correlations = {}
        for col in claim.features:
            if col not in df.columns:
                continue
            subset = df[[col, claim.target_column]].dropna()
            if len(subset) < 10:
                continue
            corr, p_val = stats.pearsonr(subset[col], subset[claim.target_column])
            correlations[col] = {"correlation": float(corr), "p_value": float(p_val)}

        return {
            "feature_correlations": correlations,
            "target_mean": float(df[claim.target_column].mean()),
            "target_std": float(df[claim.target_column].std(ddof=0)),
        }

    def _extract_coefficients(self, model) -> List[Dict[str, Any]]:
        if model is None:
            return []

        coefficients = []
        conf_int = model.conf_int()
        for name in model.params.index:
            coefficients.append(
                {
                    "name": name,
                    "coefficient": float(model.params[name]),
                    "p_value": float(model.pvalues[name]),
                    "ci_lower": float(conf_int.loc[name, 0]),
                    "ci_upper": float(conf_int.loc[name, 1]),
                }
            )
        return coefficients

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _normalize_claim(self, claim: Union[RegressiveClaim, Dict[str, Any]]) -> RegressiveClaim:
        if isinstance(claim, RegressiveClaim):
            return claim
        return RegressiveClaim(**claim)

    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        if not filters:
            return df

        filtered = df.copy()
        for column, rule in filters.items():
            if column not in filtered.columns:
                continue

            if isinstance(rule, dict):
                op = rule.get("op")
                value = rule.get("value")
                if op == "gte":
                    filtered = filtered[filtered[column] >= value]
                elif op == "gt":
                    filtered = filtered[filtered[column] > value]
                elif op == "lte":
                    filtered = filtered[filtered[column] <= value]
                elif op == "lt":
                    filtered = filtered[filtered[column] < value]
                elif op == "between":
                    low, high = rule.get("low"), rule.get("high")
                    filtered = filtered[(filtered[column] >= low) & (filtered[column] <= high)]
                elif op == "in":
                    filtered = filtered[filtered[column].isin(rule.get("values", []))]
            else:
                filtered = filtered[filtered[column] == rule]

        return filtered

    def _empty_result(
        self,
        claim: RegressiveClaim,
        status: str,
        warnings: Optional[List[str]] = None,
        sample_size: int = 0,
    ) -> Dict[str, Any]:
        return {
            "claim": asdict(claim),
            "status": status,
            "sample_size": sample_size,
            "model_summary": {},
            "coefficients": [],
            "effect_analysis": {},
            "warnings": warnings or [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _persist_result(self, result: Dict[str, Any], output_dir: Optional[Path]):
        target_dir = Path(output_dir) if output_dir else self.base_output_dir / datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"claim_{result['claim']['claim_id']}.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(self._convert_for_json(result), f, indent=2)

    def _convert_for_json(self, obj: Any):
        if isinstance(obj, dict):
            return {k: self._convert_for_json(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_for_json(v) for v in obj]
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return [self._convert_for_json(v) for v in obj.tolist()]
        return obj


DEFAULT_CLAIMS: List[RegressiveClaim] = [
    RegressiveClaim(
        claim_id="C1",
        asset_type="crypto",
        target_column="is_breakout_flag",
        target_kind="binary",
        description="Name-derived metrics reconstruct breakout probability beyond market structure controls.",
        features=[
            "syllable_count",
            "character_length",
            "memorability_score",
            "phonetic_score",
            "pronounceability_score",
            "uniqueness_score",
            "tech_tag",
            "is_optimal_syllable",
        ],
        control_features=["log_market_cap", "rank", "volume_to_cap"],
        filters={"is_active": 1},
        sample_floor=120,
        breakout_threshold=100,
    ),
    RegressiveClaim(
        claim_id="C2",
        asset_type="crypto",
        target_column="normalized_return_1yr",
        target_kind="continuous",
        description="Optimal syllable structure lifts one-year returns after standardization.",
        features=["is_optimal_syllable", "tech_tag", "memorability_score"],
        control_features=["log_market_cap", "rank"],
        filters={},
        sample_floor=120,
    ),
    RegressiveClaim(
        claim_id="D1",
        asset_type="domain",
        target_column="log_sale_price",
        target_kind="continuous",
        description="Memorability and syllabic optimization predict historical domain sale price.",
        features=[
            "syllable_count",
            "is_optimal_syllable",
            "memorability_score",
            "phonetic_score",
            "pronounceability_score",
        ],
        control_features=["tld_premium_multiplier", "brandability_score", "keyword_score"],
        filters={"sale_price": {"op": "gt", "value": 0}},
        sample_floor=20,
    ),
    # Hurricane claims
    RegressiveClaim(
        claim_id="H1",
        asset_type="hurricane",
        target_column="log_deaths",
        target_kind="continuous",
        description="Phonetically harsh hurricane names correlate with higher casualty rates after controlling for storm intensity.",
        features=[
            "phonetic_harshness_score",
            "memorability_score",
            "syllable_count",
            "gender_male",
            "sentiment_polarity",
        ],
        control_features=[
            "saffir_simpson_category",
            "max_wind_mph",
            "year",
            "is_major_hurricane",
        ],
        filters={"deaths": {"op": "gte", "value": 0}},
        sample_floor=60,
    ),
    RegressiveClaim(
        claim_id="H2",
        asset_type="hurricane",
        target_column="log_damage_usd",
        target_kind="continuous",
        description="Gender coding and memorability predict inflation-adjusted damage totals after controlling for intensity and time period.",
        features=[
            "gender_male",
            "gender_female",
            "memorability_score",
            "phonetic_harshness_score",
        ],
        control_features=[
            "saffir_simpson_category",
            "max_wind_mph",
            "year",
        ],
        filters={"damage_usd": {"op": "gt", "value": 0}},
        sample_floor=50,
    ),
    RegressiveClaim(
        claim_id="H3",
        asset_type="hurricane",
        target_column="has_casualties",
        target_kind="binary",
        description="Name memorability and harshness predict presence of casualties independent of meteorological factors.",
        features=[
            "memorability_score",
            "phonetic_harshness_score",
            "syllable_count",
            "alphabetical_position",
        ],
        control_features=[
            "saffir_simpson_category",
            "max_wind_mph",
            "decade",
        ],
        filters={},
        sample_floor=80,
    ),
    RegressiveClaim(
        claim_id="H4",
        asset_type="hurricane",
        target_column="has_major_damage",
        target_kind="binary",
        description="Phonetic features predict billion-dollar damage events beyond storm category.",
        features=[
            "phonetic_harshness_score",
            "gender_male",
            "sentiment_polarity",
            "memorability_score",
        ],
        control_features=[
            "is_major_hurricane",
            "max_wind_mph",
            "year",
        ],
        filters={},
        sample_floor=60,
    ),
    # NEW: Behavioral mediation claims
    RegressiveClaim(
        claim_id="H5",
        asset_type="hurricane",
        target_column="avoidable_death_ratio",
        target_kind="continuous",
        description="Phonetically soft names predict higher indirect:direct death ratios (worse post-storm behavior).",
        features=[
            "phonetic_harshness_score",
            "memorability_score",
            "gender_male",
        ],
        control_features=[
            "saffir_simpson_category",
            "coastal_population_exposed",
            "year",
        ],
        filters={"deaths_direct": {"op": "gt", "value": 0}, "deaths_indirect": {"op": "gte", "value": 0}},
        sample_floor=30,
    ),
    RegressiveClaim(
        claim_id="H6",
        asset_type="hurricane",
        target_column="evacuation_compliance_rate",
        target_kind="continuous",
        description="Harsh-sounding names increase evacuation compliance (actual/ordered ratio).",
        features=[
            "phonetic_harshness_score",
            "memorability_score",
            "sentiment_polarity",
        ],
        control_features=[
            "saffir_simpson_category",
            "media_mentions_prelandfall",
            "prior_hurricanes_5yr",
        ],
        filters={"evacuations_ordered": {"op": "gt", "value": 0}, "evacuations_actual": {"op": "gt", "value": 0}},
        sample_floor=20,
    ),
    RegressiveClaim(
        claim_id="H7",
        asset_type="hurricane",
        target_column="media_mentions_prelandfall",
        target_kind="continuous",
        description="Phonetically harsh and memorable names attract more pre-landfall media coverage.",
        features=[
            "phonetic_harshness_score",
            "memorability_score",
            "syllable_count",
            "uniqueness_score",
        ],
        control_features=[
            "saffir_simpson_category",
            "year",
        ],
        filters={"media_mentions_prelandfall": {"op": "gt", "value": 0}},
        sample_floor=30,
    ),
    # MTG card claims
    RegressiveClaim(
        claim_id="M1",
        asset_type="mtg",
        target_column="log_price_usd",
        target_kind="continuous",
        description="Mythic resonance and fantasy score predict legendary creature trading premium beyond rarity.",
        features=[
            "mythic_resonance_score",
            "fantasy_score",
            "memorability_score",
            "syllable_count",
            "constructed_language_score",
        ],
        control_features=[
            "rarity_tier",
            "converted_mana_cost",
            "log_edhrec_rank",
        ],
        filters={"is_legendary": 1, "is_creature": 1, "price_usd": {"op": "gt", "value": 0.5}},
        sample_floor=100,
    ),
    RegressiveClaim(
        claim_id="M2",
        asset_type="mtg",
        target_column="log_price_usd",
        target_kind="continuous",
        description="Power connotation and memorability predict instant/sorcery value controlling for playability.",
        features=[
            "power_connotation_score",
            "memorability_score",
            "phonetic_score",
            "syllable_count",
        ],
        control_features=[
            "rarity_tier",
            "converted_mana_cost",
            "log_edhrec_rank",
        ],
        filters={"is_instant_sorcery": 1, "price_usd": {"op": "gt", "value": 0.25}},
        sample_floor=80,
    ),
    RegressiveClaim(
        claim_id="M3",
        asset_type="mtg",
        target_column="is_premium",
        target_kind="binary",
        description="Fantasy and mythic resonance predict premium collectible status (>$20) with minimal playability controls.",
        features=[
            "fantasy_score",
            "mythic_resonance_score",
            "memorability_score",
            "uniqueness_score",
            "constructed_language_score",
        ],
        control_features=[
            "is_mythic",
            "log_edhrec_rank",
        ],
        filters={"price_usd": {"op": "gt", "value": 0.5}},
        sample_floor=150,
    ),
]

