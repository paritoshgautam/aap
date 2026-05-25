from dataclasses import dataclass


@dataclass(frozen=True)
class TopicDefinition:
    code: str
    title: str
    keywords: tuple[str, ...]


CHEMISTRY_TOPICS: tuple[TopicDefinition, ...] = (
    TopicDefinition("chem-stoichiometry", "Stoichiometry", ("stoichiometry", "mole", "limiting reagent", "atom economy", "empirical formula")),
    TopicDefinition("chem-atomic-structure", "Atomic structure", ("atomic structure", "electron configuration", "isotope", "ionization energy", "orbital")),
    TopicDefinition("chem-periodicity", "Periodicity", ("periodicity", "periodic trend", "electronegativity", "atomic radius", "periodic table")),
    TopicDefinition("chem-bonding", "Bonding", ("bonding", "ionic", "covalent", "metallic", "lewis", "vsepr", "intermolecular", "imf")),
    TopicDefinition("chem-energetics", "Energetics and thermochemistry", ("enthalpy", "energetics", "thermochemistry", "hess", "bond enthalpy", "calorimetry")),
    TopicDefinition("chem-kinetics", "Chemical kinetics", ("kinetics", "rate of reaction", "activation energy", "rate law", "collision theory")),
    TopicDefinition("chem-equilibrium", "Chemical equilibrium", ("equilibrium", "le chatelier", "equilibrium constant", "reaction quotient")),
    TopicDefinition("chem-acids-bases", "Acids and bases", ("acid", "base", "ph", "pka", "buffer", "titration")),
    TopicDefinition("chem-redox", "Redox processes", ("redox", "oxidation", "reduction", "electrochemical", "galvanic", "electrolysis")),
    TopicDefinition("chem-organic", "Organic chemistry", ("organic", "alkane", "alkene", "alcohol", "carboxylic", "nomenclature", "functional group")),
    TopicDefinition("chem-measurement", "Measurement and data processing", ("uncertainty", "significant figures", "data processing", "measurement", "precision", "accuracy")),
    TopicDefinition("chem-reactions", "Chemical reactions", ("chemical reaction", "reaction types", "precipitation", "neutralization", "combustion")),
    TopicDefinition("chem-solutions", "Solutions", ("solution", "solubility", "concentration", "molarity", "dilution")),
)


PHYSICS_TOPICS: tuple[TopicDefinition, ...] = (
    TopicDefinition("phys-measurement", "Measurements and uncertainties", ("measurement", "uncertainty", "error bars", "significant figures", "vectors")),
    TopicDefinition("phys-mechanics", "Mechanics", ("mechanics", "motion", "kinematics", "force", "newton", "momentum", "projectile")),
    TopicDefinition("phys-thermal", "Thermal physics", ("thermal", "temperature", "specific heat", "latent heat", "ideal gas", "kinetic model")),
    TopicDefinition("phys-waves", "Waves", ("wave", "frequency", "wavelength", "interference", "diffraction", "standing wave")),
    TopicDefinition("phys-electricity", "Electricity and magnetism", ("electric", "current", "voltage", "resistance", "circuit", "magnetic", "field")),
    TopicDefinition("phys-circular", "Circular motion and gravitation", ("circular motion", "centripetal", "gravitation", "orbital", "newton's law of gravitation")),
    TopicDefinition("phys-atomic", "Atomic, nuclear and particle physics", ("atomic", "nuclear", "radioactive", "half-life", "particle", "decay")),
    TopicDefinition("phys-energy", "Energy production", ("energy production", "power", "efficiency", "renewable", "nuclear power", "fossil")),
    TopicDefinition("phys-fields", "Fields", ("field", "gravitational field", "electric field", "potential", "field strength")),
    TopicDefinition("phys-electromagnetic-induction", "Electromagnetic induction", ("induction", "faraday", "lenz", "flux", "alternating current")),
    TopicDefinition("phys-quantum", "Quantum and nuclear physics", ("quantum", "photoelectric", "de broglie", "schrodinger", "binding energy")),
)


def topics_for_subject(subject_name: str) -> tuple[TopicDefinition, ...]:
    normalized = subject_name.lower()
    if "chem" in normalized:
        return CHEMISTRY_TOPICS
    if "phys" in normalized:
        return PHYSICS_TOPICS
    return ()
