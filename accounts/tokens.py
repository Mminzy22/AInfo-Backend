from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CreateToken(PasswordResetTokenGenerator):
    """
    Description: 유저의 pk, email_verified 와 현재시간으로 토큰을 생성

    - PasswordResetTokenGenerator 의 _make_hash_value 함수를 오버라이딩
    - 악의적인 사용자가 인증 링크를 조작하지 않도록 보호하기 위함이 목적
    - 이메일 인증 링크에 포함시킬거임
    """

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.email_verified)


token_for_verify_mail = CreateToken()
