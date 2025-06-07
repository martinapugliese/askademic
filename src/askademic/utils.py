import logging
from datetime import datetime
from typing import Tuple

import boto3
import feedparser
import pandas as pd
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.settings import ModelSettings

from askademic.constants import (
    CLAUDE_HAIKU_3_5_BEDROCK_MODEL_ID,
    CLAUDE_HAIKU_3_5_MODEL_ID,
    GEMINI_2_FLASH_MODEL_ID,
)

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


def choose_model(model_family: str = "gemini") -> Tuple[Model, ModelSettings]:
    """
    Choose the model ID based on the given model family.
    """
    if model_family not in ["gemini", "claude", "claude-aws-bedrock"]:
        raise ValueError(f"Invalid model family '{model_family}'.")

    if model_family == "gemini":
        model_name = GEMINI_2_FLASH_MODEL_ID
        model = GeminiModel(model_name=model_name)
        model_settings = ModelSettings(max_tokens=1000, temperature=0)
        return model, model_settings
    elif model_family == "claude":
        model_name = CLAUDE_HAIKU_3_5_MODEL_ID
        model = AnthropicModel(model_name=model_name)
        model_settings = ModelSettings(max_tokens=1000, temperature=0)
        return model, model_settings
    elif model_family == "claude-aws-bedrock":
        region = boto3.session.Session().region_name
        if not region:
            model_name = CLAUDE_HAIKU_3_5_BEDROCK_MODEL_ID.format(region="us")
        else:
            region = region.split("-")[0]
            model_name = CLAUDE_HAIKU_3_5_BEDROCK_MODEL_ID.format(region=region)

        model_settings = BedrockModelSettings(
            temperature=0,
            max_tokens=1000,
            top_k=1,
            bedrock_performance_configuration={"latency": "optimized"},
        )
        model = BedrockConverseModel(model_name=model_name)
        return model, model_settings


def list_categories() -> dict:
    """
    List all categories available on arXiv with their IDs
    """

    d_categories = {
        "Artificial Intelligence": "cs.AI",
        "Hardware Architecture": "cs.AR",
        "Computational Complexity": "cs.CC",
        "Computational Engineering, Finance, and Science": "cs.CE",
        "Computational Geometry": "cs.CG",
        "Computation and Language": "cs.CL",
        "Cryptography and Security": "cs.CR",
        "Computer Vision and Pattern Recognition": "cs.CV",
        "Computers and Society": "cs.CY",
        "Databases": "cs.DB",
        "Distributed, Parallel, and Cluster Computing": "cs.DC",
        "Digital Libraries": "cs.DL",
        "Discrete Mathematics": "cs.DM",
        "Data Structures and Algorithms": "cs.DS",
        "Emerging Technologies": "cs.ET",
        "Formal Languages and Automata Theory": "cs.FL",
        "General Literature": "cs.GL",
        "Graphics": "cs.GR",
        "Computer Science and Game Theory": "cs.GT",
        "Human-Computer Interaction": "cs.HC",
        "Information Retrieval": "cs.IR",
        "Information Theory": "math.IT",
        "Machine Learning": "stat.ML",
        "Logic in Computer Science": "cs.LO",
        "Multiagent Systems": "cs.MA",
        "Multimedia": "cs.MM",
        "Mathematical Software": "cs.MS",
        "Numerical Analysis": "math.NA",
        "Neural and Evolutionary Computing": "cs.NE",
        "Networking and Internet Architecture": "cs.NI",
        "Other Computer Science": "cs.OH",
        "Operating Systems": "cs.OS",
        "Performance": "cs.PF",
        "Programming Languages": "cs.PL",
        "Robotics": "cs.RO",
        "Symbolic Computation": "cs.SC",
        "Sound": "cs.SD",
        "Software Engineering": "cs.SE",
        "Social and Information Networks": "cs.SI",
        "Systems and Control": "eess.SY",
        "Econometrics": "econ.EM",
        "General Economics": "econ.GN",
        "Theoretical Economics": "econ.TH",
        "Audio and Speech Processing": "eess.AS",
        "Image and Video Processing": "eess.IV",
        "Signal Processing": "eess.SP",
        "Commutative Algebra": "math.AC",
        "Algebraic Geometry": "math.AG",
        "Analysis of PDEs": "math.AP",
        "Algebraic Topology": "math.AT",
        "Classical Analysis and ODEs": "math.CA",
        "Combinatorics": "math.CO",
        "Category Theory": "math.CT",
        "Complex Variables": "math.CV",
        "Differential Geometry": "math.DG",
        "Dynamical Systems": "math.DS",
        "Functional Analysis": "math.FA",
        "General Mathematics": "math.GM",
        "General Topology": "math.GN",
        "Group Theory": "math.GR",
        "Geometric Topology": "math.GT",
        "History and Overview": "math.HO",
        "K-Theory and Homology": "math.KT",
        "Logic": "math.LO",
        "Metric Geometry": "math.MG",
        "Mathematical Physics": "math-ph",
        "Number Theory": "math.NT",
        "Operator Algebras": "math.OA",
        "Optimization and Control": "math.OC",
        "Probability": "math.PR",
        "Quantum Algebra": "math.QA",
        "Rings and Algebras": "math.RA",
        "Representation Theory": "math.RT",
        "Symplectic Geometry": "math.SG",
        "Spectral Theory": "math.SP",
        "Statistics Theory": "stat.TH",
        "Cosmology and Nongalactic Astrophysics": "astro-ph.CO",
        "Earth and Planetary Astrophysics": "astro-ph.EP",
        "Astrophysics of Galaxies": "astro-ph.GA",
        "High Energy Astrophysical Phenomena": "astro-ph.HE",
        "Instrumentation and Methods for Astrophysics": "astro-ph.IM",
        "Solar and Stellar Astrophysics": "astro-ph.SR",
        "Disordered Systems and Neural Networks": "cond-mat.dis-nn",
        "Mesoscale and Nanoscale Physics": "cond-mat.mes-hall",
        "Materials Science": "cond-mat.mtrl-sci",
        "Other Condensed Matter": "cond-mat.other",
        "Quantum Gases": "cond-mat.quant-gas",
        "Soft Condensed Matter": "cond-mat.soft",
        "Statistical Mechanics": "cond-mat.stat-mech",
        "Strongly Correlated Electrons": "cond-mat.str-el",
        "Superconductivity": "cond-mat.supr-con",
        "General Relativity and Quantum Cosmology": "gr-qc",
        "High Energy Physics - Experiment": "hep-ex",
        "High Energy Physics - Lattice": "hep-lat",
        "High Energy Physics - Phenomenology": "hep-ph",
        "High Energy Physics - Theory": "hep-th",
        "Adaptation and Self-Organizing Systems": "nlin.AO",
        "Chaotic Dynamics": "nlin.CD",
        "Cellular Automata and Lattice Gases": "nlin.CG",
        "Pattern Formation and Solitons": "nlin.PS",
        "Exactly Solvable and Integrable Systems": "nlin.SI",
        "Nuclear Experiment": "nucl-ex",
        "Nuclear Theory": "nucl-th",
        "Accelerator Physics": "physics.acc-ph",
        "Atmospheric and Oceanic Physics": "physics.ao-ph",
        "Applied Physics": "physics.app-ph",
        "Atomic and Molecular Clusters": "physics.atm-clus",
        "Atomic Physics": "physics.atom-ph",
        "Biological Physics": "physics.bio-ph",
        "Chemical Physics": "physics.chem-ph",
        "Classical Physics": "physics.class-ph",
        "Computational Physics": "physics.comp-ph",
        "Data Analysis, Statistics and Probability": "physics.data-an",
        "Physics Education": "physics.ed-ph",
        "Fluid Dynamics": "physics.flu-dyn",
        "General Physics": "physics.gen-ph",
        "Geophysics": "physics.geo-ph",
        "History and Philosophy of Physics": "physics.hist-ph",
        "Instrumentation and Detectors": "physics.ins-det",
        "Medical Physics": "physics.med-ph",
        "Optics": "physics.optics",
        "Plasma Physics": "physics.plasm-ph",
        "Popular Physics": "physics.pop-ph",
        "Physics and Society": "physics.soc-ph",
        "Space Physics": "physics.space-ph",
        "Quantum Physics": "quant-ph",
        "Biomolecules": "q-bio.BM",
        "Cell Behavior": "q-bio.CB",
        "Genomics": "q-bio.GN",
        "Molecular Networks": "q-bio.MN",
        "Neurons and Cognition": "q-bio.NC",
        "Other Quantitative Biology": "q-bio.OT",
        "Populations and Evolution": "q-bio.PE",
        "Quantitative Methods": "q-bio.QM",
        "Subcellular Processes": "q-bio.SC",
        "Tissues and Organs": "q-bio.TO",
        "Computational Finance": "q-fin.CP",
        "Economics": "q-fin.EC",
        "General Finance": "q-fin.GN",
        "Mathematical Finance": "q-fin.MF",
        "Portfolio Management": "q-fin.PM",
        "Pricing of Securities": "q-fin.PR",
        "Risk Management": "q-fin.RM",
        "Statistical Finance": "q-fin.ST",
        "Trading and Market Microstructure": "q-fin.TR",
        "Applications": "stat.AP",
        "Computation": "stat.CO",
        "Methodology": "stat.ME",
        "Other Statistics": "stat.OT",
    }

    return d_categories


def organise_api_response_as_dataframe(response) -> pd.DataFrame:

    if not response.ok:
        logger.error(f"{datetime.now()}: No articles found")
        df_articles = pd.DataFrame()
    else:
        articles_list = feedparser.parse(response.content)["entries"]

        if len(articles_list) == 0:
            logger.error(f"{datetime.now()}: No articles found")
            df_articles = pd.DataFrame()
        else:
            logger.info(
                f"{datetime.now()}: Found {len(articles_list)} articles in the response"
            )

            df_articles = pd.DataFrame(articles_list)[
                ["id", "updated", "published", "title", "summary"]
            ]
            df_articles = df_articles.rename(columns={"summary": "abstract"})
            # change ID to PDF link
            df_articles["id"] = df_articles["id"].apply(
                lambda s: s.replace("/abs/", "/pdf/")
            )

    return df_articles
