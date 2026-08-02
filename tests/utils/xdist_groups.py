XDIST_GROUP_BY_MODULE = {
    "test_auth": "identity",
    "test_users": "identity",
    "test_ui_auth": "identity",
    "test_create_movie": "catalog_mutations",
    "test_delete_movie": "catalog_mutations",
    "test_edit_movie": "catalog_mutations",
    "test_genres": "catalog_mutations",
    "test_mock_movie": "catalog_mutations",
    "test_reviews": "catalog_mutations",
    "test_movie_details_page": "catalog_mutations",
    "test_payments": "payments",
    "test_payment_page": "payments",
}


def xdist_group_for_module(module_name: str) -> str | None:
    """Return the isolation group only for tests that share mutable external state."""
    return XDIST_GROUP_BY_MODULE.get(module_name)
