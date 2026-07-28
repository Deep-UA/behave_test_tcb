import allure
import requests

from configuration.config_parse import MAIN_API_URL, TIMEOUT_SEC

# @api scenarios skip the browser-based after_scenario hook, so this is the
# only place API traffic gets attached to the Allure report
_MAX_LOGGED_BODY_CHARS = 4000


class TcbApiClient:
    """Thin wrapper around the JSON API the TCB Vue frontend calls under /api/.
    Undocumented (no Swagger/OpenAPI), but public and unauthenticated."""

    def __init__(self, base_url: str = MAIN_API_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.response = None

    @allure.step('GET {path}')
    def _get(self, path: str, params: dict = None) -> requests.Response:
        self.response = self.session.get(f'{self.base_url}{path}', params=params, timeout=TIMEOUT_SEC)
        self._log_response()
        return self.response

    def _log_response(self):
        body = self.response.text
        if len(body) > _MAX_LOGGED_BODY_CHARS:
            body = f'{body[:_MAX_LOGGED_BODY_CHARS]}... (truncated, {len(body)} chars total)'
        allure.attach(
            f'{self.response.request.method} {self.response.url}\n'
            f'Status: {self.response.status_code} ({self.response.elapsed.total_seconds():.3f}s)\n\n'
            f'{body}',
            name='api_response',
            attachment_type=allure.attachment_type.TEXT,
        )

    def get_maintenance(self) -> requests.Response:
        return self._get('/maintenance')

    def get_filters(self) -> requests.Response:
        return self._get('/promo/filters/')

    def get_teams(self, full: bool = True) -> requests.Response:
        return self._get('/promo/teams/', params={'full': int(full)})

    def get_home(self) -> requests.Response:
        return self._get('/promo/pages/home/')

    def get_reviews(self, page: int = 1, sort_desc: int = 1, query: str = '') -> requests.Response:
        return self._get('/promo/reviews/', params={'page': page, 'sort_desc': sort_desc, 'query': query})

    def get_path(self, path: str) -> requests.Response:
        """For hitting arbitrary/unknown paths (e.g. negative 404 checks)."""
        return self._get(path)

    def json(self) -> dict:
        return self.response.json()
