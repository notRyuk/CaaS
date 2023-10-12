import CaaS.routes.static as static
import CaaS.routes.test as test
import CaaS.routes.user as user
import CaaS.routes.files as files


__all__ = [
    static.router,
    test.router,
    user.router,
    files.router
]
