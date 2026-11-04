from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoringWeights:
    """Maximum points allocated to each scoring criterion."""

    company_size: int = 25
    industry_relevance: int = 25
    contact_completeness: int = 15
    location_relevance: int = 15
    lead_source: int = 10
    business_information: int = 10

    def __post_init__(self) -> None:
        """Validate scoring weights."""

        values = (
            self.company_size,
            self.industry_relevance,
            self.contact_completeness,
            self.location_relevance,
            self.lead_source,
            self.business_information,
        )

        if any(value < 0 for value in values):
            raise ValueError("Scoring weights cannot be negative.")

        if sum(values) != 100:
            raise ValueError("Scoring weights must total exactly 100.")


@dataclass(frozen=True)
class PriorityThresholds:
    """Define score boundaries for lead priority."""

    low_max: int = 39
    medium_max: int = 69
    high_max: int = 100

    def __post_init__(self) -> None:
        if not (
            0 <= self.low_max < self.medium_max < self.high_max == 100
        ):
            raise ValueError("Invalid priority thresholds.")


@dataclass(frozen=True)
class QualificationConfig:
    """Business-specific configuration for lead qualification."""

    business_name: str

    weights: ScoringWeights = field(
        default_factory=ScoringWeights
    )

    business_information_weights: dict[str, int] = field(
        default_factory=lambda: {
            "interested_product": 5,
            "message": 5,
        }
    )

    thresholds: PriorityThresholds = field(
        default_factory=PriorityThresholds
    )

    company_size_scores: dict[str, int] = field(
        default_factory=dict
    )

    target_industries: frozenset[str] = frozenset()

    target_locations: frozenset[str] = frozenset()

    lead_source_scores: dict[str, int] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate business-specific scoring configuration."""

        if any(
            score < 0 or score > self.weights.company_size
            for score in self.company_size_scores.values()
        ):
            raise ValueError("Invalid company-size scoring value.")

        if any(
            score < 0 or score > self.weights.lead_source
            for score in self.lead_source_scores.values()
        ):
            raise ValueError("Invalid lead-source scoring value.")

        if any(
            score < 0
            for score in self.business_information_weights.values()
        ):
            raise ValueError(
                "Business-information scores cannot be negative."
            )

        if sum(self.business_information_weights.values()) != (
            self.weights.business_information
        ):
            raise ValueError(
                "Business-information scores must equal their configured weight."
            )


APEXFLOW_CONFIG = QualificationConfig(
    business_name="ApexFlow Solutions",

    company_size_scores={
        "1-10": 5,
        "11-50": 10,
        "51-200": 15,
        "201-500": 20,
        "501-1000": 23,
        "1000+": 25,
    },

    target_industries=frozenset({
        "manufacturing",
        "professional services",
        "financial services",
        "healthcare",
        "retail",
        "logistics",
        "information technology",
        "education",
    }),

    # Intentionally empty until ApexFlow's service geography
    # is defined. The scoring engine must flag this as
    # unconfigured rather than silently assuming relevance.

    target_locations=frozenset(),

    lead_source_scores={
        "referral": 10,
        "website": 8,
        "direct": 7,
        "campaign": 5,
        "social_media": 4,
        "other": 2,
    },
)