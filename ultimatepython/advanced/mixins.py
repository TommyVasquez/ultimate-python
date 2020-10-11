from abc import ABC, abstractmethod


class Request:
    """Request model."""
    def __init__(self, url, user):
        self.url = url
        self.user = user


class RequestHandler(ABC):
    """Request handler interface."""
    @abstractmethod
    def handle(self, request):
        raise NotImplementedError


class TemplateHandlerMixin(RequestHandler):
    """Abstract template mixin for RequestHandler."""
    template_suffix = ".template"
    failure_content = "Not found"

    def handle(self, request):
        template_name = self.get_template_name(request.url)
        if self.is_valid_template(template_name):
            return self.render_template(template_name)
        return self.failure_content

    def get_template_name(self, request_url):
        raise NotImplementedError

    def is_valid_template(self, template_name):
        return template_name.endswith(self.template_suffix)

    def render_template(self, template_name):
        raise NotImplementedError


class AuthHandlerMixin(RequestHandler):
    """Abstract auth mixin for RequestHandler."""
    success_content = "Something private"
    failure_content = "Access denied"

    def handle(self, request):
        if self.is_valid_user(request.user):
            return self.success_content
        return self.failure_content

    def is_valid_user(self, request_user):
        raise NotImplementedError


class SimpleTemplateHandler(TemplateHandlerMixin):
    """Concrete template handler."""
    def __init__(self, template_prefix, template_content):
        self.template_prefix = template_prefix
        self.template_content = template_content

    def get_template_name(self, request_url):
        return request_url[1:]

    def is_valid_template(self, template_name):
        if not super().is_valid_template(template_name):
            return False
        return template_name.startswith(self.template_prefix)

    def render_template(self, template_name):
        return self.template_content


class AdminHandler(AuthHandlerMixin):
    """Concrete auth handler."""
    success_content = "Admin stuff"

    def __init__(self, authorized_users):
        self.authorized_users = authorized_users

    def is_valid_user(self, request_user):
        return request_user in self.authorized_users


def main():
    welcome_handler = SimpleTemplateHandler("welcome", "Hello world")
    assert welcome_handler.handle(Request("/welcome.template", "nobody")) == "Hello world"
    assert welcome_handler.handle(Request("/foo.bar", "nobody")) == "Not found"

    admin_handler = AdminHandler({"john", "jane"})
    assert admin_handler.handle(Request("/admin.html", "john")) == "Admin stuff"
    assert admin_handler.handle(Request("/admin.html", "nobody")) == "Access denied"


if __name__ == '__main__':
    main()
