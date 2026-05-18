"""
Detects when the agent's reasoning drifts away from the original task.
Uses cosine distance between original task embedding and current step embedding.
Fires a correction prompt if drift > threshold. Hard resets after 2 consecutive drifts.
"""
from dataclasses import dataclass
import numpy as np
from backend.rag_engine.embeddings import embed_query
from loguru import logger


@dataclass
class DriftSignal:
    drifted: bool
    drift_score: float
    correction_prompt: str = ""


class GoalAnchor:
    CHECK_EVERY = 3       # check every N steps
    DRIFT_THRESHOLD = 0.28  # cosine distance (0 = identical, 1 = opposite)
    HARD_RESET_AFTER = 2   # consecutive drifts before hard reset

    def __init__(self, original_task: str):
        self.original_task = original_task
        self.original_embedding = np.array(embed_query(original_task))
        self._consecutive_drifts = 0

    def check(self, step_num: int, current_reasoning: str) -> DriftSignal:
        # Only check every CHECK_EVERY steps
        if step_num % self.CHECK_EVERY != 0:
            return DriftSignal(drifted=False, drift_score=0.0)

        current_emb = np.array(embed_query(current_reasoning))

        # Cosine distance = 1 - cosine_similarity
        dot = np.dot(self.original_embedding, current_emb)
        norm = np.linalg.norm(self.original_embedding) * np.linalg.norm(current_emb)
        cosine_sim = dot / (norm + 1e-8)
        drift_score = float(1.0 - cosine_sim)

        if drift_score > self.DRIFT_THRESHOLD:
            self._consecutive_drifts += 1
            logger.warning(f"Goal drift detected: score={drift_score:.3f}, consecutive={self._consecutive_drifts}")

            if self._consecutive_drifts >= self.HARD_RESET_AFTER:
                correction = (
                    f"⚠️ HARD GOAL RESET — You have drifted from the task TWICE.\n"
                    f"STOP. Return to the original task:\n"
                    f"'{self.original_task}'\n"
                    f"Your next action MUST directly address this task. "
                    f"Use write_note to record what you've found so far, then continue."
                )
                self._consecutive_drifts = 0
            else:
                correction = (
                    f"⚠️ GOAL DRIFT WARNING (score={drift_score:.2f})\n"
                    f"Original task: '{self.original_task}'\n"
                    f"Your current reasoning seems off-track. "
                    f"How does your current step directly serve the original task?"
                )

            return DriftSignal(drifted=True, drift_score=drift_score, correction_prompt=correction)

        self._consecutive_drifts = 0
        return DriftSignal(drifted=False, drift_score=drift_score)
