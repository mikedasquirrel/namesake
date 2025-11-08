"""BandMembersCollector - Individual Band Member Data Collection

Collects individual band member data for nominative determinism research.
Links to existing Band data and collects member roles, names, and biographical info.

Research Focus:
- Name-role correlation (bassist vs drummer vs vocalist)
- Collective name composition → band success
- Temporal evolution of name-role patterns

Data Source: MusicBrainz API (band member relationships)

Author: Michael Smerconish
Date: November 2025
"""

import logging
import time
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.models import db, BandMember, BandMemberAnalysis, Band
from core.research_framework import FRAMEWORK
from utils.progress_tracker import ProgressTracker
from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer

logger = logging.getLogger(__name__)


class BandMembersCollector:
    """Collector for individual band member data"""
    
    def __init__(self):
        """Initialize collector"""
        self.domain_meta = FRAMEWORK.get_domain('band_members')
        self.musicbrainz_base_url = "https://musicbrainz.org/ws/2"
        self.rate_limit_seconds = 1.0  # MusicBrainz requirement
        
        # User agent (required by MusicBrainz)
        self.headers = {
            'User-Agent': 'NominativeDeterminismResearch/1.0 (research@nominative-determinism.org)'
        }
        
        # Analyzers for linguistic features
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def collect_sample(self, target_size: int = 3000) -> Dict:
        """
        Collect band member data from existing bands in database.
        
        Strategy:
        1. Query Band table for existing bands
        2. For each band, get members from MusicBrainz
        3. Extract roles and biographical info
        4. Perform linguistic analysis on member names
        5. Store in BandMember and BandMemberAnalysis tables
        
        Args:
            target_size: Target number of members to collect
        
        Returns:
            Collection statistics
        """
        logger.info(f"Starting band member collection (target: {target_size})...")
        
        # Get existing bands from database (use id only to avoid column issues)
        try:
            bands = Band.query.limit(500).all()
        except Exception as e:
            logger.error(f"Error querying bands: {e}")
            # Fallback: query only basic columns
            bands = db.session.query(Band.id, Band.name).limit(500).all()
        
        logger.info(f"Found {len(bands)} bands in database to extract members from")
        
        if len(bands) == 0:
            logger.error("No bands found in database. Run band collection first.")
            return {
                'total_collected': 0,
                'total_updated': 0,
                'total_errors': 1,
                'errors': ['No bands in database'],
                'timestamp': datetime.now().isoformat()
            }
        
        tracker = ProgressTracker(
            total_steps=min(target_size, len(bands) * 5),  # Estimate ~5 members per band
            print_interval=50,
            task_name="Band Member Collection"
        )
        
        collected = 0
        updated = 0
        analyzed = 0
        errors = []
        bands_processed = 0
        
        try:
            for band in bands:
                if collected >= target_size:
                    logger.info(f"Reached target size of {target_size} members")
                    break
                
                try:
                    # Get members from MusicBrainz
                    members_data = self._fetch_band_members(band.id, band.name)
                    
                    if not members_data:
                        continue
                    
                    # Process each member
                    for member_data in members_data:
                        if collected >= target_size:
                            break
                        
                        try:
                            # Check if member already exists
                            existing = BandMember.query.filter_by(
                                name=member_data['name'],
                                band_id=band.id
                            ).first()
                            
                            if existing:
                                # Update existing record
                                self._update_member(existing, member_data)
                                updated += 1
                            else:
                                # Create new member
                                member = BandMember(
                                    name=member_data['name'],
                                    band_id=band.id,
                                    primary_role=member_data.get('primary_role'),
                                    secondary_roles=json.dumps(member_data.get('secondary_roles', [])),
                                    is_songwriter=member_data.get('is_songwriter', False),
                                    is_lead_vocalist=member_data.get('is_lead_vocalist', False),
                                    is_founding_member=member_data.get('is_founding_member', False),
                                    nationality=member_data.get('nationality'),
                                    years_active_start=member_data.get('years_active_start'),
                                    years_active_end=member_data.get('years_active_end')
                                )
                                db.session.add(member)
                                db.session.flush()  # Get member.id
                                
                                # Perform linguistic analysis
                                analysis_data = self._analyze_member_name(member.name)
                                analysis = BandMemberAnalysis(
                                    member_id=member.id,
                                    **analysis_data
                                )
                                db.session.add(analysis)
                                
                                collected += 1
                                analyzed += 1
                            
                            # Commit periodically
                            if (collected + updated) % 50 == 0:
                                db.session.commit()
                                tracker.update(50, message=f"Members: {collected}, Bands: {bands_processed}")
                            
                        except Exception as e:
                            logger.error(f"Error processing member {member_data.get('name')}: {e}")
                            errors.append(f"Member {member_data.get('name')}: {str(e)}")
                    
                    bands_processed += 1
                    
                    # Rate limiting
                    time.sleep(self.rate_limit_seconds)
                    
                except Exception as e:
                    logger.error(f"Error processing band {band.name}: {e}")
                    errors.append(f"Band {band.name}: {str(e)}")
            
            # Final commit
            db.session.commit()
            
            tracker.complete(f"Collection complete: {collected} new members from {bands_processed} bands")
            
            return {
                'total_collected': collected,
                'total_updated': updated,
                'total_analyzed': analyzed,
                'bands_processed': bands_processed,
                'total_errors': len(errors),
                'errors': errors[:20],  # First 20 errors
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            tracker.error(str(e))
            db.session.rollback()
            raise
    
    def collect_stratified_sample(self, target_per_role: Dict[str, int]) -> Dict:
        """
        Collect stratified sample by role.
        
        Args:
            target_per_role: Dict mapping role to target count
        
        Returns:
            Collection statistics
        """
        logger.info("Starting stratified band member collection...")
        logger.info(f"Targets: {target_per_role}")
        
        # First, collect general sample
        total_target = sum(target_per_role.values())
        result = self.collect_sample(target_size=total_target * 2)  # Oversample
        
        # Check distribution
        role_counts = {}
        for role in target_per_role.keys():
            count = BandMember.query.filter_by(primary_role=role).count()
            role_counts[role] = count
        
        logger.info("Role distribution:")
        for role, count in role_counts.items():
            target = target_per_role.get(role, 0)
            logger.info(f"  {role}: {count}/{target} ({count/target*100 if target else 0:.1f}%)")
        
        result['role_distribution'] = role_counts
        result['stratification_targets'] = target_per_role
        
        return result
    
    def _fetch_band_members(self, band_id: str, band_name: str) -> List[Dict]:
        """
        Fetch band members from MusicBrainz API.
        
        Args:
            band_id: MusicBrainz band ID
            band_name: Band name (for logging)
        
        Returns:
            List of member dictionaries
        """
        try:
            # Query MusicBrainz for artist relationships
            url = f"{self.musicbrainz_base_url}/artist/{band_id}"
            params = {
                'inc': 'artist-rels',
                'fmt': 'json'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"MusicBrainz API returned {response.status_code} for {band_name}")
                return []
            
            data = response.json()
            relations = data.get('relations', [])
            
            members = []
            
            # Extract member relationships
            for relation in relations:
                if relation.get('type') in ['member of band', 'founder', 'conductor']:
                    artist = relation.get('artist', {})
                    
                    member_data = {
                        'name': artist.get('name'),
                        'musicbrainz_id': artist.get('id'),
                        'primary_role': self._extract_primary_role(relation),
                        'secondary_roles': self._extract_secondary_roles(relation),
                        'is_songwriter': 'songwriter' in str(relation).lower(),
                        'is_lead_vocalist': 'lead' in str(relation).lower() and 'vocal' in str(relation).lower(),
                        'is_founding_member': relation.get('type') == 'founder',
                        'years_active_start': self._extract_year(relation.get('begin')),
                        'years_active_end': self._extract_year(relation.get('end'))
                    }
                    
                    if member_data['name']:
                        members.append(member_data)
            
            logger.info(f"Found {len(members)} members for {band_name}")
            return members
            
        except Exception as e:
            logger.error(f"Error fetching members for {band_name}: {e}")
            return []
    
    def _extract_primary_role(self, relation: Dict) -> Optional[str]:
        """Extract primary role from relation data"""
        # MusicBrainz uses attributes for instruments
        attributes = relation.get('attributes', [])
        
        # Priority order for role determination
        role_mapping = {
            'vocals': 'vocalist',
            'lead vocals': 'vocalist',
            'guitar': 'guitarist',
            'lead guitar': 'guitarist',
            'bass': 'bassist',
            'bass guitar': 'bassist',
            'drums': 'drummer',
            'percussion': 'drummer',
            'keyboard': 'keyboardist',
            'piano': 'keyboardist',
            'synthesizer': 'keyboardist'
        }
        
        for attr in attributes:
            attr_lower = attr.lower()
            for key, role in role_mapping.items():
                if key in attr_lower:
                    return role
        
        # Default to vocalist if no instrument specified but member of band
        return 'vocalist'
    
    def _extract_secondary_roles(self, relation: Dict) -> List[str]:
        """Extract all roles from relation data"""
        attributes = relation.get('attributes', [])
        
        roles = []
        role_mapping = {
            'vocals': 'vocalist',
            'guitar': 'guitarist',
            'bass': 'bassist',
            'drums': 'drummer',
            'keyboard': 'keyboardist',
            'songwriter': 'songwriter',
            'composer': 'composer'
        }
        
        for attr in attributes:
            attr_lower = attr.lower()
            for key, role in role_mapping.items():
                if key in attr_lower and role not in roles:
                    roles.append(role)
        
        return roles
    
    def _extract_year(self, date_str: Optional[str]) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        try:
            # Try full date first
            if len(date_str) >= 4:
                return int(date_str[:4])
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _update_member(self, member: BandMember, data: Dict):
        """Update existing member record"""
        member.primary_role = data.get('primary_role', member.primary_role)
        member.secondary_roles = json.dumps(data.get('secondary_roles', []))
        member.is_songwriter = data.get('is_songwriter', member.is_songwriter)
        member.is_lead_vocalist = data.get('is_lead_vocalist', member.is_lead_vocalist)
        member.is_founding_member = data.get('is_founding_member', member.is_founding_member)
        member.years_active_start = data.get('years_active_start', member.years_active_start)
        member.years_active_end = data.get('years_active_end', member.years_active_end)
        member.last_updated = datetime.utcnow()
    
    def _analyze_member_name(self, name: str) -> Dict:
        """
        Perform linguistic analysis on member name.
        
        Args:
            name: Member name
        
        Returns:
            Dictionary of analysis features
        """
        try:
            # Basic analysis
            basic = self.name_analyzer.analyze(name)
            
            # Phonetic features
            phonemic = self.phonemic_analyzer.analyze(name)
            
            # Determine name origin (simplified)
            name_origin = self._determine_name_origin(name)
            stage_name = self._is_stage_name(name)
            
            return {
                'syllable_count': basic.get('syllable_count', 0),
                'character_length': basic.get('character_length', 0),
                'phonetic_harshness': phonemic.get('harshness_score', 0.0),
                'phonetic_smoothness': phonemic.get('softness_score', 0.0),
                'memorability_score': basic.get('memorability_score', 0.0),
                'uniqueness_score': basic.get('uniqueness_score', 0.0),
                'pronounceability_score': basic.get('pronounceability_score', 0.0),
                'name_origin': name_origin,
                'stage_name_indicator': stage_name,
                'vowel_ratio': phonemic.get('vowel_ratio', 0.0),
                'consonant_cluster_score': phonemic.get('consonant_cluster_complexity', 0.0),
                'phonetic_features_json': json.dumps(phonemic)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing name '{name}': {e}")
            return {
                'syllable_count': len(name.split()),
                'character_length': len(name),
                'phonetic_harshness': 0.0,
                'phonetic_smoothness': 0.0,
                'memorability_score': 0.0
            }
    
    def _determine_name_origin(self, name: str) -> str:
        """Determine name origin (simplified heuristic)"""
        # This is a simplified heuristic - could be enhanced with actual name database
        name_lower = name.lower()
        
        # Nordic indicators
        if any(x in name_lower for x in ['björn', 'øy', 'ø', 'å', 'lars', 'sven', 'thor']):
            return 'Nordic'
        
        # Italian indicators
        if name.endswith(('i', 'o', 'ello', 'etti')):
            return 'Italian'
        
        # Germanic indicators
        if any(x in name_lower for x in ['schmidt', 'müller', 'hans', 'wolfgang']):
            return 'Germanic'
        
        # Default
        return 'Anglo'
    
    def _is_stage_name(self, name: str) -> bool:
        """Heuristic to detect if name is likely a stage name"""
        # Single word names often stage names
        if ' ' not in name.strip():
            return True
        
        # Unusual capitalization
        if name.count(' ') == 1:
            parts = name.split()
            if all(p.islower() or p.isupper() for p in parts):
                return True
        
        # Known stage name patterns
        stage_indicators = ['The', 'DJ', 'MC', 'Lil', 'Big', 'Young']
        if any(name.startswith(ind) for ind in stage_indicators):
            return True
        
        return False
    
    def collect_from_band_list(self, band_ids: List[str]) -> Dict:
        """
        Collect members from specific list of bands.
        
        Args:
            band_ids: List of band IDs to collect members from
        
        Returns:
            Collection statistics
        """
        logger.info(f"Collecting members from {len(band_ids)} specific bands...")
        
        tracker = ProgressTracker(
            total_steps=len(band_ids),
            print_interval=10,
            task_name="Targeted Band Member Collection"
        )
        
        collected = 0
        updated = 0
        analyzed = 0
        errors = []
        
        for band_id in band_ids:
            try:
                band = Band.query.get(band_id)
                if not band:
                    logger.warning(f"Band {band_id} not found in database")
                    continue
                
                members_data = self._fetch_band_members(band_id, band.name)
                
                for member_data in members_data:
                    try:
                        existing = BandMember.query.filter_by(
                            name=member_data['name'],
                            band_id=band_id
                        ).first()
                        
                        if existing:
                            self._update_member(existing, member_data)
                            updated += 1
                        else:
                            member = BandMember(
                                name=member_data['name'],
                                band_id=band_id,
                                primary_role=member_data.get('primary_role'),
                                secondary_roles=json.dumps(member_data.get('secondary_roles', [])),
                                is_songwriter=member_data.get('is_songwriter', False),
                                is_lead_vocalist=member_data.get('is_lead_vocalist', False)
                            )
                            db.session.add(member)
                            db.session.flush()
                            
                            analysis_data = self._analyze_member_name(member.name)
                            analysis = BandMemberAnalysis(member_id=member.id, **analysis_data)
                            db.session.add(analysis)
                            
                            collected += 1
                            analyzed += 1
                    
                    except Exception as e:
                        logger.error(f"Error processing member: {e}")
                        errors.append(str(e))
                
                tracker.update(1, message=f"Collected: {collected}, Updated: {updated}")
                time.sleep(self.rate_limit_seconds)
                
            except Exception as e:
                logger.error(f"Error processing band {band_id}: {e}")
                errors.append(str(e))
        
        db.session.commit()
        tracker.complete()
        
        return {
            'total_collected': collected,
            'total_updated': updated,
            'total_analyzed': analyzed,
            'total_errors': len(errors),
            'errors': errors[:10],
            'timestamp': datetime.now().isoformat()
        }
