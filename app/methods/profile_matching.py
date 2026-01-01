"""
methods/profile_matching.py - Profile Matching Method
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ProfileMatching:
    """Profile Matching Method Implementation"""
    
    @staticmethod
    def calculate(decision_matrix: np.ndarray,
                 weights: np.ndarray,
                 alternatives: List[str],
                 ideal_profile: np.ndarray) -> Dict:
        """
        Profile Matching Method:
        Compares each alternative against an ideal profile
        
        Formula:
        1. Calculate gap between alternative and ideal for each criterion
        2. Calculate weighted gap
        3. Rank by smallest total gap (or highest similarity)
        
        Args:
            decision_matrix: MxN decision matrix
            weights: Weight vector
            alternatives: Alternative names
            ideal_profile: Ideal values for each criterion
            
        Returns:
            Results dictionary
        """
        m, n = decision_matrix.shape
        decision_matrix = decision_matrix.astype(float)
        ideal_profile = ideal_profile.astype(float)
        
        # Step 1: Calculate gaps (differences from ideal)
        gaps = np.zeros((m, n))
        weighted_gaps = np.zeros((m, n))
        
        for i in range(m):
            for j in range(n):
                gap = abs(decision_matrix[i, j] - ideal_profile[j])
                gaps[i, j] = gap
                weighted_gaps[i, j] = weights[j] * gap
        
        # Step 2: Calculate total weighted gap
        total_gaps = np.sum(weighted_gaps, axis=1)
        
        # Step 3: Convert gap to similarity score (lower gap = higher score)
        # Normalize gaps to 0-100 scale (100 = perfect match, 0 = worst match)
        max_gap = np.max(total_gaps)
        if max_gap > 0:
            similarity_scores = 100 * (1 - (total_gaps / max_gap))
        else:
            similarity_scores = np.ones(m) * 100
        
        # Step 4: Rank by similarity (highest score = best)
        rankings = np.argsort(similarity_scores)[::-1]
        
        results = {
            'method': 'Profile Matching',
            'ideal_profile': [float(p) for p in ideal_profile],
            'gaps': gaps.tolist(),
            'weighted_gaps': weighted_gaps.tolist(),
            'total_gaps': [float(g) for g in total_gaps],
            'similarity_scores': [float(s) for s in similarity_scores],
            'scores': [float(s) for s in similarity_scores],
            'rankings': [int(r+1) for r in rankings],
            'alternative_rankings': {alternatives[r]: int(i+1) for i, r in enumerate(rankings)},
            'best_alternative': alternatives[rankings[0]],
            'best_score': float(similarity_scores[rankings[0]]),
            'worst_alternative': alternatives[rankings[-1]],
            'worst_score': float(similarity_scores[rankings[-1]]),
            'calculation_steps': {
                'gap_formula': '|Alternative_value - Ideal_value|',
                'weighted_gap_formula': 'w_j × gap_ij',
                'total_gap_formula': 'Σ(weighted_gaps)',
                'similarity_formula': '100 × (1 - total_gap / max_gap)',
                'detailed_calculations': []
            }
        }
        
        # Detailed steps
        for i in range(m):
            calc = {
                'alternative': alternatives[i],
                'gaps': [float(g) for g in gaps[i]],
                'weighted_gaps': [float(wg) for wg in weighted_gaps[i]],
                'total_gap': float(total_gaps[i]),
                'similarity_score': float(similarity_scores[i]),
                'ranking': int(np.where(rankings == i)[0][0] + 1)
            }
            results['calculation_steps']['detailed_calculations'].append(calc)
        
        return results


def calculate_profile_matching(decision_matrix: np.ndarray,
                              weights: np.ndarray,
                              alternatives: List[str],
                              ideal_profile: np.ndarray) -> Dict:
    """Calculate Profile Matching method"""
    return ProfileMatching.calculate(decision_matrix, weights, alternatives, ideal_profile)

