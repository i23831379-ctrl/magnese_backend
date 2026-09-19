# Import all model modules to ensure they are registered with SQLAlchemy Base metadata

from .user import User
from .project import Project
from .study_area import StudyArea
from .dataset import Dataset
from .target import ExplorationTarget
from .field_note import FieldNote
from .prospectivity_zone import ProspectivityZone
from .geological_layer import GeologicalLayer
from .geochemical_sample import GeochemicalSample
from .remote_sensing_layer import RemoteSensingLayer
from .model_run import ModelRun
from .prediction import Prediction
from .evidence import Evidence
from .target_ranking import TargetRanking
from .audit_log import AuditLog
from .upload_record import UploadRecord
