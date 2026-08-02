from tests.utils.xdist_groups import xdist_group_for_module


def test_identity_and_catalog_mutations_have_distinct_groups() -> None:
    assert xdist_group_for_module("test_auth") == "identity"
    assert xdist_group_for_module("test_users") == "identity"
    assert xdist_group_for_module("test_create_movie") == "catalog_mutations"
    assert xdist_group_for_module("test_reviews") == "catalog_mutations"


def test_read_only_modules_are_not_serialized() -> None:
    assert xdist_group_for_module("test_get_movies") is None
    assert xdist_group_for_module("test_get_movie_by_id") is None
