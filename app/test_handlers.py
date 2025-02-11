import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from handlers import UserHandler
from models import UserDB
from schemas import UserCreate, UserResponse

@pytest.fixture
def mock_db():
    """Fixture to create a mock database session."""
    return MagicMock(spec=Session)

@pytest.fixture
def user_handler(mock_db):
    """Fixture to create a UserHandler instance with a mocked DB session."""
    return UserHandler(mock_db)

@pytest.fixture
def sample_user():
    """Fixture for a sample user."""
    return UserCreate(
        first_name="John",
        last_name="Doe",
        nickname="johnd",
        email="john@example.com",
        password="securepass"
    )

@pytest.fixture
def sample_user_db():
    """Fixture for a sample UserDB object (SQLAlchemy model)."""
    return UserDB(
        id=1,
        first_name="John",
        last_name="Doe",
        nickname="johnd",
        email="john@example.com",
        password="hashed_password"
    )

# ✅ TEST CREATE USER
def test_create_user(user_handler, mock_db, sample_user, sample_user_db):
    """Test user creation"""
    mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda user: setattr(user, "id", 1)  # Simulate DB refresh

    result = user_handler.create_user(sample_user)

    assert isinstance(result, UserResponse)
    assert result.id == 1
    assert result.first_name == sample_user.first_name
    assert result.email == sample_user.email

# ✅ TEST GET USER
def test_get_user(user_handler, mock_db, sample_user_db):
    """Test retrieving a user"""
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_db

    result = user_handler.get_user(1)

    assert isinstance(result, UserResponse)
    assert result.id == sample_user_db.id
    assert result.email == sample_user_db.email

# ✅ TEST UPDATE USER
def test_update_user(user_handler, mock_db, sample_user, sample_user_db):
    """Test updating a user"""
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_db
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = user_handler.update_user(1, sample_user)

    assert isinstance(result, UserResponse)
    assert result.id == 1
    assert result.first_name == sample_user.first_name

# ✅ TEST DELETE USER
def test_delete_user(user_handler, mock_db, sample_user_db):
    """Test deleting a user"""
    mock_db.query.return_value.filter.return_value.first.return_value = sample_user_db
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None

    result = user_handler.delete_user(1)

    assert result == {"message": "User deleted successfully"}

# ✅ TEST LIST USERS
def test_list_users(user_handler, mock_db, sample_user_db):
    """Test listing users"""
    mock_db.query.return_value.all.return_value = [sample_user_db]

    result = user_handler.list_users()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].email == sample_user_db.email
