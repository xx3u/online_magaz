from flask import abort, redirect, url_for, request
from flask_admin.contrib.peewee import ModelView
from flask_security import current_user


class AuthMixin:
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(
                    url_for(
                        'security.login',
                        next=request.url
                    )
                )


class Admin(AuthMixin, ModelView):
    pass
