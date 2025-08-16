import pytest
from authenticator import Authenticator  # クラス定義ファイル名に合わせて変更

# 1) register() でユーザーが正しく登録されるか
def test_register_success():
    auth = Authenticator()
    auth.register("alice", "secret")
    assert auth.users.get("alice") == "secret"

# 2) register() で既存ユーザー名だと例外 + メッセージ
def test_register_duplicate_user_raises():
    auth = Authenticator()
    auth.register("alice", "secret")
    with pytest.raises(ValueError) as excinfo:
        auth.register("alice", "another")
    assert str(excinfo.value) == "エラー: ユーザーは既に存在します。"

# 3) login() で正しいユーザー名とパスワードならログインできるか
def test_login_success():
    auth = Authenticator()
    auth.register("alice", "secret")
    msg = auth.login("alice", "secret")
    assert msg == "ログイン成功"

# 4) login() で誤ったパスワードなら例外 + メッセージ
def test_login_wrong_password_raises():
    auth = Authenticator()
    auth.register("alice", "secret")
    with pytest.raises(ValueError) as excinfo:
        auth.login("alice", "wrong")
    assert str(excinfo.value) == "エラー: ユーザー名またはパスワードが正しくありません。"