class TestAuthentication:

    def test_registered_user_can_login(self, new_registered_user):
        api_manager, user_credentials = new_registered_user

        login_response = api_manager.auth_api.login(
            email=user_credentials["email"],
            password=user_credentials["password"],
            expected_status=200
        )
        login_data = login_response.json()

        assert "accessToken" in login_data, "Ответ на логин должен содержать accessToken"
        assert "user" in login_data, "Ответ на логин должен содержать объект пользователя"

        user_object = login_data["user"]
        assert user_object["email"] == user_credentials["email"]
        assert user_object["fullName"] == user_credentials["fullName"]
        assert user_object["roles"] == ["USER"]
        assert user_object["verified"] is True
        assert user_object["banned"] is False
        assert "id" in user_object
        assert "createdAt" in user_object 