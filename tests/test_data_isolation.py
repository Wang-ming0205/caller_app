# #測試資料隔離
# from uuid import uuid4

# def create_staff_and_get_headers(
#     client,
#     admin_headers,
#     username,
#     password,
# ):
#     """建立 staff 使用者並登入，回傳該使用者的 JWT Header。"""
#     create_response = client.post(
#         "/api/users",
#         headers=admin_headers,
#         json={
#             "username": username,
#             "password": password,
#             "full_name": f"pytest {username}",
#             "role": "staff",
#             "is_active": True,
#         },
#     )
#     assert create_response.status_code in (200, 201)
#     login_response = client.post(
#         "/api/auth/login",
#         json={
#             "username": username,
#             "password": password,
#         },
#     )
#     assert login_response.status_code == 200
#     access_token = login_response.json()["access_token"]
#     return {
#         "Authorization": f"Bearer {access_token}",
#     }


# def test_customer_data_isolation_between_users(client, auth_headers):
#     """
#     使用者 A 建立的客戶只能由 A 存取，使用者 B 不應看到該客戶。
#     """
#     unique_value = uuid4().hex[:8]
#     password = "testpass123"
#     user_a_headers = create_staff_and_get_headers(
#         client=client,
#         admin_headers=auth_headers,
#         username=f"staff_a_{unique_value}",
#         password=password,
#     )
#     user_b_headers = create_staff_and_get_headers(
#         client=client,
#         admin_headers=auth_headers,
#         username=f"staff_b_{unique_value}",
#         password=password,
#     )
#     phone_number = f"09{uuid4().int % 100_000_000:08d}"
#     create_customer_response = client.post(
#         "/api/customers",
#         headers=user_a_headers,
#         json={
#             "name": "使用者 A 的客戶",
#             "phone_number": phone_number,
#             "note": "資料隔離測試",
#         },
#     )
#     assert create_customer_response.status_code in (200, 201)
#     customer = create_customer_response.json()
#     customer_id = customer["id"]
#     # 使用者 A 是資料擁有者，應該可以查到客戶。
#     owner_response = client.get(
#         f"/api/customers/{customer_id}",
#         headers=user_a_headers,
#     )
#     assert owner_response.status_code == 200
#     assert owner_response.json()["id"] == customer_id
#     # 使用者 B 的客戶列表不應出現使用者 A 的客戶。
#     other_user_list_response = client.get(
#         "/api/customers/",
#         headers=user_b_headers,
#     )
#     assert other_user_list_response.status_code == 200
#     assert all(
#         item["id"] != customer_id
#         for item in other_user_list_response.json()
#     )
#     # 即使使用者 B 知道 customer_id，也不應取得該客戶。
#     # 後端回傳 404，避免洩漏這筆資料確實存在。
#     other_user_get_response = client.get(
#         f"/api/customers/{customer_id}",
#         headers=user_b_headers,
#     )
#     assert other_user_get_response.status_code == 404
#     assert other_user_get_response.json()["detail"] == "Customer not found"

    