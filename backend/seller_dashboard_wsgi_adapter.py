"""Optional WSGI wrapper for a trusted read-only dashboard backend."""
import json
from urllib.parse import parse_qs
from .seller_dashboard_http_session_bridge import handle_cookie_authenticated_dashboard


def create_wsgi_dashboard(load_session, load_membership, query_inventory_by_seller):
    """Create an unmounted WSGI application with injected trusted loaders."""
    def app(environ, start_response):
        if environ.get("PATH_INFO") != "/api/seller/dashboard":
            code, body = 404, {"error": "not_found"}
        else:
            try:
                query = parse_qs(environ.get("QUERY_STRING", ""), max_num_fields=10)
                if set(query) - {"seller_id", "status", "low_stock_threshold"}:
                    raise ValueError("unknown query parameter")
                if any(len(values) != 1 for values in query.values()):
                    raise ValueError("duplicate query parameter")
                threshold = int(query.get("low_stock_threshold", ["5"])[0])
                code, body = handle_cookie_authenticated_dashboard(
                    method=environ.get("REQUEST_METHOD"),
                    cookie_header=environ.get("HTTP_COOKIE"),
                    seller_id=query.get("seller_id", [""])[0],
                    status=query.get("status", ["all"])[0],
                    low_stock_threshold=threshold,
                    load_session=load_session,
                    load_membership=load_membership,
                    query_inventory_by_seller=query_inventory_by_seller,
                )
            except (TypeError, ValueError):
                code, body = 400, {"error": "invalid_query"}
        payload = json.dumps(body).encode("utf-8")
        reason = {200: "OK", 400: "Bad Request", 403: "Forbidden",
                  404: "Not Found", 405: "Method Not Allowed",
                  503: "Service Unavailable"}.get(code, "Error")
        headers = [("Content-Type", "application/json"),
                   ("Cache-Control", "no-store"),
                   ("Content-Length", str(len(payload)))]
        if code == 405:
            headers.append(("Allow", "GET"))
        start_response(f"{code} {reason}", headers)
        return [payload]
    return app
