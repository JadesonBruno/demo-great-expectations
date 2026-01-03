# Import standard libs
from pathlib import Path

# Import third-party libs
import great_expectations as gx
import pandas as pd
from great_expectations.core.run_identifier import RunIdentifier
from great_expectations.exceptions import DataContextError

# Load data with pandas
module_root = Path(__file__).parent.parent
csv_path = module_root / "data" / "dataset.csv"
df = pd.read_csv(csv_path)


# Initialize Great Expectations context
context = gx.get_context(mode="file")


# Get or create a Pandas data source
try:
    data_source = context.data_sources.get("pandas")
except KeyError:
    data_source = context.data_sources.add_pandas(name="pandas")

# Get or create a Data Asset
try:
    data_asset = data_source.get_asset("pd_dataframe_asset")
except LookupError:
    data_asset = data_source.add_dataframe_asset(name="pd_dataframe_asset")

# Get or create a Batch Definition
try:
    batch_definition = data_asset.get_batch_definition("batch_definition")
except KeyError:
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        "batch_definition"
    )


# Get or Create Expectation Suite
try:
    suite = context.suites.get("expectation")
except DataContextError:
    suite = context.suites.add(
        gx.core.expectation_suite.ExpectationSuite(name="expectation")
    )

    # Expectation for column "id" to exist
    suite.add_expectation(
        gx.expectations.ExpectColumnToExist(
            column="id",
            severity="critical",
            notes={"notes": "Identifier each employee"},
        )
    )

    # Expectation for table column count to be between 1 and 3
    suite.add_expectation(
        gx.expectations.ExpectTableColumnCountToBeBetween(
            min_value=1, max_value=3, severity="critical"
        )
    )

    # Expectation for table row count to be between 1 and 100
    suite.add_expectation(
        gx.expectations.ExpectTableRowCountToBeBetween(
            min_value=1, max_value=100, severity="critical"
        )
    )

    # Expectation for column "id" values to not be null
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="id", severity="critical")
    )

    # Expectation for column "id" values to be between 1 and 10
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="id", min_value=1, max_value=10, severity="critical"
        )
    )

    # Expectation for column "id" values to be unique
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(column="id", severity="critical")
    )

    # Expectation for unique value count in column "id" to be between 1 and 10
    suite.add_expectation(
        gx.expectations.ExpectColumnUniqueValueCountToBeBetween(
            column="id", min_value=1, max_value=10, severity="critical"
        )
    )


# Get or Create Validation Definition
try:
    validation_definition = context.validation_definitions.get("validation_definition")
except DataContextError:
    validation_definition = context.validation_definitions.add(
        gx.core.validation_definition.ValidationDefinition(
            name="validation_definition",
            data=batch_definition,
            suite=suite,
        )
    )


# Configure Data Docs site if not already configured
base_directory = "uncommitted/data_docs/local_site/"
site_config = {
    "class_name": "SiteBuilder",
    "site_index_builder": {
        "class_name": "DefaultSiteIndexBuilder",
    },
    "store_backend": {
        "class_name": "TupleFilesystemStoreBackend",
        "base_directory": base_directory,
    },
}

site_name = "my_data_docs_site"
try:
    context.add_data_docs_site(
        site_name=site_name,
        site_config=site_config,
    )
except DataContextError:
    pass


actions = [
    gx.checkpoint.actions.UpdateDataDocsAction(
        name="update_my_site",
        site_names=[site_name],
    )
]

# Get or Create or retrieve Checkpoint
try:
    checkpoint = context.checkpoints.get("checkpoint")
except DataContextError:
    checkpoint = context.checkpoints.add(
        gx.checkpoint.checkpoint.Checkpoint(
            name="checkpoint",
            validation_definitions=[validation_definition],
            actions=actions,
        )
    )


# Run Checkpoint
checkpoint_result = checkpoint.run(
    batch_parameters={"dataframe": df},
    run_id=RunIdentifier(
        run_name=f"demo_run_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    ),
)
print(checkpoint_result.describe())


# Open Data Docs in browser automatically
context.open_data_docs()
