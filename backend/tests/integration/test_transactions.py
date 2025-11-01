"""
Integration tests for transaction API endpoints.

Tests the full transaction CRUD flow including:
- List transactions with pagination and filtering
- Create transaction
- Get transaction by ID
- Update transaction
- Delete transaction
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi import status


class TestListTransactions:
    """Tests for GET /api/v1/transactions endpoint."""

    def test_list_empty_transactions(self, client, auth_headers):
        """Test listing transactions when user has none."""
        response = client.get("/api/v1/transactions/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_transactions_basic(self, client, auth_headers, db, test_user):
        """Test listing user's transactions."""
        from app.models.transaction import Transaction

        # Create test transactions
        trans1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Groceries",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        trans2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("1000.00"),
            description="Salary",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        db.add_all([trans1, trans2])
        db.commit()

        response = client.get("/api/v1/transactions/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["description"] in ["Groceries", "Salary"]
        assert data[1]["description"] in ["Groceries", "Salary"]

    def test_list_transactions_pagination(self, client, auth_headers, db, test_user):
        """Test pagination works correctly."""
        from app.models.transaction import Transaction

        # Create 5 transactions
        for i in range(5):
            trans = Transaction(
                user_id=test_user.id,
                amount=Decimal(f"{(i+1)*10}.00"),
                description=f"Transaction {i+1}",
                type="expense",
                category="Shopping",
                transaction_date=date.today() - timedelta(days=i)
            )
            db.add(trans)
        db.commit()

        # Get first 2
        response = client.get("/api/v1/transactions/?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

        # Get next 2
        response = client.get("/api/v1/transactions/?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_list_transactions_filter_by_type(self, client, auth_headers, db, test_user):
        """Test filtering by transaction type."""
        from app.models.transaction import Transaction

        # Create mixed transactions
        expense = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Expense",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        income = Transaction(
            user_id=test_user.id,
            amount=Decimal("1000.00"),
            description="Income",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        db.add_all([expense, income])
        db.commit()

        # Filter for expenses only
        response = client.get("/api/v1/transactions/?type=expense", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "expense"

        # Filter for income only
        response = client.get("/api/v1/transactions/?type=income", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "income"

    def test_list_transactions_filter_by_category(self, client, auth_headers, db, test_user):
        """Test filtering by category."""
        from app.models.transaction import Transaction

        trans1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Food",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        trans2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="Clothes",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add_all([trans1, trans2])
        db.commit()

        response = client.get("/api/v1/transactions/?category=Shopping", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Shopping"

    def test_list_transactions_user_isolation(self, client, auth_headers, db, test_user, test_user_2):
        """Test users only see their own transactions."""
        from app.models.transaction import Transaction

        # Create transactions for both users
        trans1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="User 1 Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        trans2 = Transaction(
            user_id=test_user_2.id,
            amount=Decimal("100.00"),
            description="User 2 Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add_all([trans1, trans2])
        db.commit()

        # User 1 should only see their transaction
        response = client.get("/api/v1/transactions/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "User 1 Transaction"

    def test_list_transactions_without_auth(self, client):
        """Test listing transactions without authentication fails."""
        response = client.get("/api/v1/transactions/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateTransaction:
    """Tests for POST /api/v1/transactions endpoint."""

    def test_create_transaction_success(self, client, auth_headers):
        """Test creating a valid transaction."""
        response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 50.00,
                "description": "Lunch",
                "type": "expense",
                "category": "Food & Dining",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["amount"] == "50.00"
        assert data["description"] == "Lunch"
        assert data["type"] == "expense"
        assert data["category"] == "Food & Dining"
        assert "id" in data
        assert "created_at" in data

    def test_create_transaction_invalid_category(self, client, auth_headers):
        """Test creating transaction with invalid category fails."""
        response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 50.00,
                "description": "Test",
                "type": "expense",
                "category": "Invalid Category",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "category" in response.json()["detail"].lower()

    def test_create_transaction_missing_required_field(self, client, auth_headers):
        """Test creating transaction without required field fails."""
        response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 50.00,
                # Missing description
                "type": "expense",
                "category": "Shopping",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transaction_invalid_type(self, client, auth_headers):
        """Test creating transaction with invalid type fails."""
        response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 50.00,
                "description": "Test",
                "type": "invalid",
                "category": "Shopping",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transaction_negative_amount(self, client, auth_headers):
        """Test creating transaction with negative amount fails."""
        response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": -50.00,
                "description": "Test",
                "type": "expense",
                "category": "Shopping",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transaction_without_auth(self, client):
        """Test creating transaction without authentication fails."""
        response = client.post(
            "/api/v1/transactions/",
            json={
                "amount": 50.00,
                "description": "Test",
                "type": "expense",
                "category": "Shopping",
                "transaction_date": str(date.today())
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetTransaction:
    """Tests for GET /api/v1/transactions/{id} endpoint."""

    def test_get_transaction_success(self, client, auth_headers, db, test_user):
        """Test getting a specific transaction."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.get(f"/api/v1/transactions/{trans.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == trans.id
        assert data["description"] == "Test Transaction"
        assert data["amount"] == "50.00"

    def test_get_nonexistent_transaction(self, client, auth_headers):
        """Test getting non-existent transaction returns 404."""
        response = client.get("/api/v1/transactions/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_user_transaction(self, client, auth_headers, db, test_user_2):
        """Test getting another user's transaction returns 404."""
        from app.models.transaction import Transaction

        # Create transaction for user 2
        trans = Transaction(
            user_id=test_user_2.id,
            amount=Decimal("50.00"),
            description="User 2 Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        # Try to access as user 1
        response = client.get(f"/api/v1/transactions/{trans.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_transaction_without_auth(self, client, db, test_user):
        """Test getting transaction without authentication fails."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.get(f"/api/v1/transactions/{trans.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateTransaction:
    """Tests for PUT /api/v1/transactions/{id} endpoint."""

    def test_update_transaction_success(self, client, auth_headers, db, test_user):
        """Test updating a transaction."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Original",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.put(
            f"/api/v1/transactions/{trans.id}",
            headers=auth_headers,
            json={
                "description": "Updated",
                "amount": 75.00
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated"
        assert data["amount"] == "75.00"
        assert data["type"] == "expense"  # Unchanged fields remain

    def test_update_partial_fields(self, client, auth_headers, db, test_user):
        """Test updating only some fields."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Original",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.put(
            f"/api/v1/transactions/{trans.id}",
            headers=auth_headers,
            json={"description": "Just description updated"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Just description updated"
        assert data["amount"] == "50.00"  # Unchanged

    def test_update_nonexistent_transaction(self, client, auth_headers):
        """Test updating non-existent transaction returns 404."""
        response = client.put(
            "/api/v1/transactions/99999",
            headers=auth_headers,
            json={"description": "Updated"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_user_transaction(self, client, auth_headers, db, test_user_2):
        """Test updating another user's transaction returns 404."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user_2.id,
            amount=Decimal("50.00"),
            description="User 2",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.put(
            f"/api/v1/transactions/{trans.id}",
            headers=auth_headers,
            json={"description": "Hacked"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_transaction_invalid_category(self, client, auth_headers, db, test_user):
        """Test updating with invalid category fails."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.put(
            f"/api/v1/transactions/{trans.id}",
            headers=auth_headers,
            json={"category": "Invalid Category"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_transaction_without_auth(self, client, db, test_user):
        """Test updating transaction without authentication fails."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.put(
            f"/api/v1/transactions/{trans.id}",
            json={"description": "Updated"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteTransaction:
    """Tests for DELETE /api/v1/transactions/{id} endpoint."""

    def test_delete_transaction_success(self, client, auth_headers, db, test_user):
        """Test deleting a transaction."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="To Delete",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)
        trans_id = trans.id

        response = client.delete(f"/api/v1/transactions/{trans_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/api/v1/transactions/{trans_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_transaction(self, client, auth_headers):
        """Test deleting non-existent transaction returns 404."""
        response = client.delete("/api/v1/transactions/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_user_transaction(self, client, auth_headers, db, test_user_2):
        """Test deleting another user's transaction returns 404."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user_2.id,
            amount=Decimal("50.00"),
            description="User 2",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.delete(f"/api/v1/transactions/{trans.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_transaction_without_auth(self, client, db, test_user):
        """Test deleting transaction without authentication fails."""
        from app.models.transaction import Transaction

        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        response = client.delete(f"/api/v1/transactions/{trans.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTransactionWorkflows:
    """Integration tests for complete transaction workflows."""

    def test_full_crud_workflow(self, client, auth_headers):
        """Test complete CRUD workflow: create, read, update, delete."""
        # Create
        create_response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 100.00,
                "description": "Test Transaction",
                "type": "expense",
                "category": "Shopping",
                "transaction_date": str(date.today())
            }
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        trans_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/api/v1/transactions/{trans_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["description"] == "Test Transaction"

        # Update
        update_response = client.put(
            f"/api/v1/transactions/{trans_id}",
            headers=auth_headers,
            json={"description": "Updated Transaction"}
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["description"] == "Updated Transaction"

        # Delete
        delete_response = client.delete(f"/api/v1/transactions/{trans_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_after_delete = client.get(f"/api/v1/transactions/{trans_id}", headers=auth_headers)
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND

    def test_create_multiple_and_list(self, client, auth_headers):
        """Test creating multiple transactions and listing them."""
        # Create 3 transactions
        for i in range(3):
            response = client.post(
                "/api/v1/transactions/",
                headers=auth_headers,
                json={
                    "amount": (i + 1) * 10.00,
                    "description": f"Transaction {i+1}",
                    "type": "expense",
                    "category": "Shopping",
                    "transaction_date": str(date.today())
                }
            )
            assert response.status_code == status.HTTP_201_CREATED

        # List all
        list_response = client.get("/api/v1/transactions/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == 3
