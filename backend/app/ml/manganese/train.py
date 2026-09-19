"""Optional Random Forest training workflow for validated manganese data."""

from dataclasses import dataclass
from datetime import date
from typing import Any

from .preprocessing import DEFAULT_FEATURES, build_feature_matrix
from .training import ManganeseTrainingRecord
from .model import ModelMetadata


@dataclass(frozen=True)
class TrainingResult:
    model_name: str
    version: str
    training_date: str
    feature_list: list[str]
    record_count: int
    metrics: dict[str, float]
    status: str
    estimator: Any

    def metadata(self, dataset_name: str) -> ModelMetadata:
        return ModelMetadata(
            model_name=self.model_name,
            version=self.version,
            training_date=self.training_date,
            feature_list=self.feature_list,
            training_dataset=dataset_name,
            record_count=self.record_count,
            metrics=self.metrics,
            status=self.status,
        )


def train_manganese_random_forest(
    records: list[ManganeseTrainingRecord],
    *,
    feature_names: tuple[str, ...] = DEFAULT_FEATURES,
) -> TrainingResult:
    """Train only on supplied validated data and return measured holdout metrics."""
    if len(records) < 10:
        raise ValueError("at least 10 labelled manganese records are required for training")
    if len({record.label for record in records}) < 2:
        raise ValueError("training data must contain both label classes 0 and 1")

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
        from sklearn.model_selection import train_test_split
    except ImportError as error:
        raise RuntimeError(
            "scikit-learn is required to train the manganese model; install backend requirements first"
        ) from error

    matrix, labels = build_feature_matrix(records, feature_names)
    train_x, test_x, train_y, test_y = train_test_split(
        matrix, labels, test_size=0.2, random_state=42, stratify=labels
    )
    estimator = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    estimator.fit(train_x, train_y)
    predictions = estimator.predict(test_x)
    probabilities = estimator.predict_proba(test_x)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(test_y, predictions)),
        "precision": float(precision_score(test_y, predictions, zero_division=0)),
        "recall": float(recall_score(test_y, predictions, zero_division=0)),
        "f1": float(f1_score(test_y, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(test_y, probabilities)),
    }
    return TrainingResult(
        model_name="Manganese Random Forest",
        version="0.1",
        training_date=date.today().isoformat(),
        feature_list=list(feature_names),
        record_count=len(records),
        metrics=metrics,
        status="trained-not-field-validated",
        estimator=estimator,
    )
