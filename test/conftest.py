import pytest
import logging
import sys
import os

# IMPORTANT: Set test environment BEFORE any imports
os.environ['ENVIRONMENT'] = 'test'
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.database_manager import DBManager as dbm
import database.database as db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Hook that runs BEFORE any tests"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests requiring database"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    
    # Database verification
    logger.info("="*60)
    logger.info("PYTEST CONFIGURATION")
    logger.info("="*60)
    logger.info(f"Environment: {os.getenv('ENVIRONMENT')}")
    logger.info(f"Database: {db.MONGODB_DATABASE}")
    logger.info(f"Database name: {db.db.name}")
    logger.info("="*60)

    # Safety check
    assert "test" in db.db.name.lower(), \
        f"WARNING: Not using test database! Current: {db.db.name}"
    logger.info("✓ Safety check passed: Using test database")


@pytest.fixture(scope="session", autouse=True)
def verify_test_environment():
    """
    Session-wide fixture - runs ONCE before all tests.
    Auto-used so it always runs even if not requested.
    """
    logger.info("\n Verifying test environment...")
    logger.info(f"   Database: {db.db.name}")
    
    assert os.getenv('ENVIRONMENT') == 'test', "ENVIRONMENT must be 'test'"
    assert 'test' in db.db.name.lower(), f"Must use test database, got: {db.db.name}"
    
    logger.info("✓ All safety checks passed!")
    
    yield
    
    logger.info("\n🧹 Test session complete ✅")