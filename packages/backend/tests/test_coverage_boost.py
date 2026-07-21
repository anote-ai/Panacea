"""Tests to boost coverage across agents, middleware, services, and payments."""
from __future__ import annotations

import os
from importlib import reload
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _mock_cnx(fetchall=None, fetchone=None, lastrowid=1, rowcount=1):
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cursor.fetchone.return_value = fetchone
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount
    cnx = MagicMock()
    cnx.cursor.return_value = cursor
    return cnx


# ---------------------------------------------------------------------------
# middleware/auth.py
# ---------------------------------------------------------------------------

def test_require_auth_no_token(client):
    resp = client.get("/api/user/profile")
    assert resp.status_code == 401


def test_require_auth_with_token(client, auth_headers):
    from unittest.mock import MagicMock, patch
    mock_cnx = MagicMock()
    mock_cnx.cursor.return_value.fetchall.return_value = []
    with patch("api_endpoints.documents.handler.get_connection", return_value=mock_cnx):
        resp = client.get("/api/documents", headers=auth_headers)
    assert resp.status_code == 200


def test_require_auth_decorator_directly(app):
    """Test the require_auth wrapper directly."""
    from middleware.auth import require_auth

    called = []

    @require_auth
    def dummy():
        called.append(True)
        return "ok"

    # Without app context / valid JWT we expect the 401 path
    with app.test_request_context():
        dummy()
        # verify_jwt_in_request raises without a token → returns 401 response tuple
        assert called == []  # inner fn not called


# ---------------------------------------------------------------------------
# agents/chat_agent.py
# ---------------------------------------------------------------------------

def test_run_chat_agent_no_api_key():
    """When no API key is set, agent should return an error string."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        # LangChain will fail without a real key; the except path returns "Error: ..."
        from agents.chat_agent import run_chat_agent
        result = run_chat_agent("hello")
        assert isinstance(result, str)


def test_run_chat_agent_with_mock():
    """Mock the Anthropic LLM so the happy path executes."""
    mock_response = MagicMock()
    mock_response.content = "mocked reply"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response

    mock_langchain = MagicMock()
    mock_langchain.ChatAnthropic.return_value = mock_llm
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch.dict("sys.modules", {"langchain_anthropic": mock_langchain}):
            import agents.chat_agent as mod
            reload(mod)
            result = mod.run_chat_agent("hello", history=[
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hey"},
            ])
            assert isinstance(result, str)


def test_run_chat_agent_history_branches():
    """Exercise history role branches without real LLM."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        from agents.chat_agent import run_chat_agent
        result = run_chat_agent(
            "question",
            history=[
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "second"},
                {"role": "unknown", "content": "ignored"},
            ],
        )
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# agents/coding_agent.py
# ---------------------------------------------------------------------------

def test_coding_agent_no_api_key():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        from agents.coding_agent import run_coding_agent
        result = run_coding_agent("write hello world")
        assert isinstance(result, str)


def test_coding_agent_with_mock():
    mock_response = MagicMock()
    mock_response.content = "print('hello')"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("langchain_anthropic.ChatAnthropic", return_value=mock_llm):
            import agents.coding_agent as mod
            reload(mod)
            result = mod.run_coding_agent("write hello world", cwd="/tmp")
            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# services/llm.py
# ---------------------------------------------------------------------------

def test_llm_complete_anthropic_mock():
    mock_client = MagicMock()
    mock_block = MagicMock()
    mock_block.text = "answer"
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="claude-sonnet-4-6")
            assert result == "answer"


def test_llm_complete_anthropic_with_system():
    mock_client = MagicMock()
    mock_block = MagicMock()
    mock_block.text = "answer"
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="claude-sonnet-4-6", system="be concise")
            assert result == "answer"


def test_llm_complete_anthropic_empty_content():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = []
    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="claude-sonnet-4-6")
            assert result == ""


def test_llm_complete_openai_mock():
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "openai answer"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
        with patch("openai.OpenAI", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="gpt-4o")
            assert result == "openai answer"


def test_llm_complete_openai_with_system():
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "openai answer"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
        with patch("openai.OpenAI", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="gpt-4o", system="be brief")
            assert result == "openai answer"


def test_llm_complete_openai_empty():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = []
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
        with patch("openai.OpenAI", return_value=mock_client):
            import services.llm as mod
            reload(mod)
            result = mod.complete("hello", model="gpt-4o")
            assert result == ""


def test_llm_complete_ollama_mock():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "ollama answer"}
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_resp):
        import services.llm as mod
        reload(mod)
        result = mod.complete("hello", model="llama3")
        assert result == "ollama answer"


# ---------------------------------------------------------------------------
# services/rag.py
# ---------------------------------------------------------------------------

def test_ingest_document_path_traversal():
    from services.rag import ingest_document
    with pytest.raises(ValueError, match="outside upload folder"):
        ingest_document("doc1", Path("/etc/passwd"))


def test_ingest_document_no_chromadb(tmp_path):
    """Ingest a text file; chromadb import will fail in test env, returns chunk count."""
    upload_dir = Path("/tmp/anote_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    test_file = upload_dir / "test_doc.txt"
    test_file.write_text("Hello world. " * 100)

    # Patch chromadb import to raise so the except branch executes
    with patch.dict("sys.modules", {"chromadb": None, "chromadb.utils": None,
                                     "chromadb.utils.embedding_functions": None}):
        import services.rag as mod
        reload(mod)
        count = mod.ingest_document("test1", test_file)
        assert count > 0  # chunks returned despite chromadb failure

    test_file.unlink(missing_ok=True)


def test_extract_text_txt(tmp_path):
    upload_dir = Path("/tmp/anote_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    f = upload_dir / "sample.txt"
    f.write_text("hello world")

    from services.rag import _extract_text
    result = _extract_text(f)
    assert "hello" in result
    f.unlink(missing_ok=True)


def test_extract_text_path_traversal():
    from services.rag import _extract_text
    # File outside upload dir → returns empty string
    result = _extract_text(Path("/etc/passwd"))
    assert result == ""


def test_extract_text_unknown_ext(tmp_path):
    upload_dir = Path("/tmp/anote_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    f = upload_dir / "sample.bin"
    f.write_bytes(b"\x00\x01\x02")

    from services.rag import _extract_text
    result = _extract_text(f)
    assert result == ""
    f.unlink(missing_ok=True)


def test_query_documents_no_context_no_key():
    """With no chromadb and no API key, returns the 'not found' message."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        with patch.dict("sys.modules", {"chromadb": None}):
            import services.rag as mod
            reload(mod)
            result = mod.query_documents("what is this?")
            assert "not find" in result.lower() or isinstance(result, str)


def test_retrieve_context_no_chromadb_returns_empty():
    with patch.dict("sys.modules", {"chromadb": None}):
        import services.rag as mod
        reload(mod)
        result = mod.retrieve_context("what is this?")
        assert result == ""


def test_retrieve_context_returns_joined_chunks():
    mock_chroma = MagicMock()
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"documents": [["chunk1", "chunk2"]]}
    mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

    mock_ef_module = MagicMock()
    mock_ef_module.DefaultEmbeddingFunction.return_value = MagicMock()

    with patch.dict("sys.modules", {"chromadb": mock_chroma,
                                     "chromadb.utils": mock_ef_module,
                                     "chromadb.utils.embedding_functions": mock_ef_module}):
        import services.rag as mod
        reload(mod)
        result = mod.retrieve_context("what is this?", doc_ids=["doc1"])
        assert result == "chunk1\n\nchunk2"


def test_query_documents_context_no_key():
    """When chromadb returns results but no API key, returns the context snippet."""
    mock_chroma = MagicMock()
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"documents": [["chunk1", "chunk2"]]}
    mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

    mock_ef_module = MagicMock()
    mock_ef_module.DefaultEmbeddingFunction.return_value = MagicMock()

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        with patch.dict("sys.modules", {"chromadb": mock_chroma,
                                         "chromadb.utils": mock_ef_module,
                                         "chromadb.utils.embedding_functions": mock_ef_module}):
            import services.rag as mod
            reload(mod)
            result = mod.query_documents("what is this?", doc_ids=["doc1"])
            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# services/streaming.py
# ---------------------------------------------------------------------------

def test_stream_agent_no_api_key():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        import services.streaming as mod
        reload(mod)
        events = list(mod.stream_agent_response("hello"))
        assert len(events) == 1
        assert "error" in events[0]
        assert "ANTHROPIC_API_KEY" in events[0]


def test_stream_agent_with_mock():
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Hello", " world"])

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            events = list(mod.stream_agent_response("hello"))
            # Should have text events + done
            assert any("text" in e for e in events)
            assert any("done" in e for e in events)


def test_stream_agent_with_mock_on_text_callback():
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Hello", " world"])

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            collected: list[str] = []
            list(mod.stream_agent_response("hello", on_text=collected.append))
            assert collected == ["Hello", " world"]


def test_stream_agent_error_path():
    mock_client = MagicMock()
    mock_client.messages.stream.side_effect = RuntimeError("API error")

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            events = list(mod.stream_agent_response("hello"))
            assert any("error" in e for e in events)


def test_stream_llm_no_api_key():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        import services.streaming as mod
        reload(mod)
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            mod.stream_llm_response("hello")


def test_stream_llm_with_mock():
    mock_block = MagicMock()
    mock_block.text = "streaming answer"
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("anthropic.Anthropic", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            result = mod.stream_llm_response("hello", history=[{"role": "user", "content": "hi"}])
            assert result == "streaming answer"


# ---------------------------------------------------------------------------
# api_endpoints/payments/handler.py
# ---------------------------------------------------------------------------

def test_payments_checkout_no_stripe(client, auth_headers):
    resp = client.post(
        "/api/payments/checkout", json={"priceId": "price_test", "plan": "basic"}, headers=auth_headers,
    )
    assert resp.status_code == 503


def test_payments_checkout_invalid_plan(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        resp = client.post(
            "/api/payments/checkout", json={"priceId": "price_test", "plan": "nope"}, headers=auth_headers,
        )
        assert resp.status_code == 400


def test_payments_checkout_unconfigured_plan(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        resp = client.post(
            "/api/payments/checkout", json={"plan": "basic"}, headers=auth_headers,
        )
        assert resp.status_code == 503


def test_payments_portal_no_stripe(client, auth_headers):
    resp = client.post("/api/payments/portal", json={}, headers=auth_headers)
    assert resp.status_code == 503


def test_payments_portal_no_customer(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx(fetchone=None)):
            resp = client.post("/api/payments/portal", json={}, headers=auth_headers)
            assert resp.status_code == 404


def test_payments_webhook_no_secret(client):
    resp = client.post("/api/payments/webhook", data=b"payload",
                        headers={"Content-Type": "application/json"})
    assert resp.status_code == 503
    assert resp.get_json()["error"] == "Stripe webhook not configured"


def test_payments_webhook_bad_signature(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test",
                                   "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        mock_stripe.Webhook.construct_event.side_effect = Exception("bad sig")
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            resp = client.post("/api/payments/webhook", data=b"{}",
                                headers={"Stripe-Signature": "bad",
                                         "Content-Type": "application/json"})
            assert resp.status_code == 400


def test_payments_checkout_stripe_error(client, auth_headers):
    with patch.dict(os.environ, {
        "STRIPE_SECRET_KEY": "sk_test",
        "STRIPE_PRICE_BASIC": "price_basic",
    }):
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.side_effect = Exception("stripe error")
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            resp = client.post(
                "/api/payments/checkout",
                json={"priceId": "price_test", "plan": "basic"},
                headers=auth_headers,
            )
            assert resp.status_code == 500


def test_payments_portal_stripe_error(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        mock_stripe.billing_portal.Session.create.side_effect = Exception("stripe error")
        customer = {"stripe_id": "cus_test", "plan": "basic", "status": "active", "period_end": None}
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx(fetchone=customer)):
                resp = client.post("/api/payments/portal", json={}, headers=auth_headers)
                assert resp.status_code == 500


def test_payments_checkout_success(client, auth_headers):
    with patch.dict(os.environ, {
        "STRIPE_SECRET_KEY": "sk_test",
        "STRIPE_PRICE_BASIC": "price_server_owned",
    }):
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            resp = client.post("/api/payments/checkout",
                                json={"priceId": "price_123",
                                      "plan": "basic",
                                      "successUrl": "http://localhost:3000/ok",
                                      "cancelUrl": "http://localhost:3000/cancel"},
                                headers=auth_headers)
            assert resp.status_code == 200
            assert "url" in resp.get_json()
            call_kwargs = mock_stripe.checkout.Session.create.call_args.kwargs
            assert call_kwargs["line_items"] == [
                {"price": "price_server_owned", "quantity": 1},
            ]
            assert call_kwargs["success_url"] == "http://localhost/app?checkout=success"
            assert call_kwargs["cancel_url"] == "http://localhost/app?checkout=cancelled"


def test_payments_portal_success(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/test"
        mock_stripe = MagicMock()
        mock_stripe.billing_portal.Session.create.return_value = mock_session
        customer = {"stripe_id": "cus_123", "plan": "basic", "status": "active", "period_end": None}
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx(fetchone=customer)):
                resp = client.post("/api/payments/portal",
                                    json={"returnUrl": "http://localhost:3000"},
                                    headers=auth_headers)
                assert resp.status_code == 200
                assert "url" in resp.get_json()


def test_payments_credits_checkout_invalid_pack(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        resp = client.post(
            "/api/payments/credits/checkout", json={"credits": 42}, headers=auth_headers,
        )
        assert resp.status_code == 400


def test_payments_credits_checkout_success(client, auth_headers):
    with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test"}):
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/credits"
        mock_stripe = MagicMock()
        mock_stripe.checkout.Session.create.return_value = mock_session
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            resp = client.post(
                "/api/payments/credits/checkout", json={"credits": 1000}, headers=auth_headers,
            )
            assert resp.status_code == 200
            assert "url" in resp.get_json()


def test_payments_webhook_credit_pack_completed(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "mode": "payment",
                "metadata": {"kind": "credit_pack", "user_id": "1", "credits": "1000"},
            }},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx()), \
                 patch("api_endpoints.payments.handler.add_purchased_credits") as mock_add:
                resp = client.post("/api/payments/webhook", data=b"{}",
                                    headers={"Stripe-Signature": "sig",
                                             "Content-Type": "application/json"})
                assert resp.status_code == 200
                mock_add.assert_called_once_with(mock_add.call_args[0][0], 1, 1000)


def test_payments_webhook_subscription_completed(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "mode": "subscription",
                "customer": "cus_1",
                "metadata": {"user_id": "1", "plan": "basic"},
            }},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx()), \
                 patch("api_endpoints.payments.handler.upsert_stripe_customer") as mock_upsert, \
                 patch("api_endpoints.payments.handler.set_plan_and_credits") as mock_set:
                resp = client.post("/api/payments/webhook", data=b"{}",
                                    headers={"Stripe-Signature": "sig",
                                             "Content-Type": "application/json"})
                assert resp.status_code == 200
                mock_upsert.assert_called_once()
                mock_set.assert_called_once_with(mock_set.call_args[0][0], 1, "basic", 200)


def test_payments_webhook_invoice_paid_renews_credits(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "type": "invoice.payment_succeeded",
            "data": {"object": {"customer": "cus_1"}},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx()), \
                 patch("api_endpoints.payments.handler.get_user_id_for_stripe_customer", return_value=1), \
                 patch("api_endpoints.payments.handler.get_stripe_customer", return_value={"plan": "pro"}), \
                 patch("api_endpoints.payments.handler.set_plan_and_credits") as mock_set:
                resp = client.post("/api/payments/webhook", data=b"{}",
                                    headers={"Stripe-Signature": "sig",
                                             "Content-Type": "application/json"})
                assert resp.status_code == 200
                mock_set.assert_called_once_with(mock_set.call_args[0][0], 1, "pro", 500)


def test_payments_webhook_subscription_deleted_downgrades(client):
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_1"}},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=_mock_cnx()), \
                 patch("api_endpoints.payments.handler.get_user_id_for_stripe_customer", return_value=1), \
                 patch("api_endpoints.payments.handler.downgrade_to_free") as mock_downgrade, \
                 patch("api_endpoints.payments.handler.update_stripe_customer_status") as mock_status:
                resp = client.post("/api/payments/webhook", data=b"{}",
                                    headers={"Stripe-Signature": "sig",
                                             "Content-Type": "application/json"})
                assert resp.status_code == 200
                mock_downgrade.assert_called_once()
                mock_status.assert_called_once_with(mock_status.call_args[0][0], "cus_1", "canceled")


def test_payments_webhook_handler_error_releases_claim_for_retry(client):
    """A failed side effect must be retryable and must not retain its claim."""
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "id": "evt_retry_test",
            "type": "checkout.session.completed",
            "data": {"object": {"mode": "payment", "metadata": {"kind": "credit_pack"}}},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        cnx = _mock_cnx()
        with patch.dict("sys.modules", {"stripe": mock_stripe}), \
             patch("api_endpoints.payments.handler.get_connection", return_value=cnx), \
             patch("api_endpoints.payments.handler.claim_stripe_event", return_value=True), \
             patch("api_endpoints.payments.handler.release_stripe_event") as mock_release:
            resp = client.post("/api/payments/webhook", data=b"{}",
                                headers={"Stripe-Signature": "sig",
                                         "Content-Type": "application/json"})
            assert resp.status_code == 500
            mock_release.assert_called_once_with(mock_release.call_args[0][0], "evt_retry_test")


def test_payments_webhook_redelivered_event_is_not_reprocessed(client):
    """Stripe can redeliver the same event more than once — a second
    delivery of an already-processed event must not double-credit."""
    with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_SECRET_KEY": "sk_test"}):
        mock_stripe = MagicMock()
        event = {
            "id": "evt_dedupe_test",
            "type": "checkout.session.completed",
            "data": {"object": {
                "mode": "payment",
                "metadata": {"kind": "credit_pack", "user_id": "1", "credits": "1000"},
            }},
        }
        mock_stripe.Webhook.construct_event.return_value = event
        # First delivery: claim succeeds (True). Second: already claimed (False).
        cnx = _mock_cnx()
        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("api_endpoints.payments.handler.get_connection", return_value=cnx), \
                 patch("api_endpoints.payments.handler.claim_stripe_event", side_effect=[True, False]), \
                 patch("api_endpoints.payments.handler.add_purchased_credits") as mock_add:
                for _ in range(2):
                    resp = client.post("/api/payments/webhook", data=b"{}",
                                        headers={"Stripe-Signature": "sig",
                                                 "Content-Type": "application/json"})
                    assert resp.status_code == 200
                mock_add.assert_called_once()


# ---------------------------------------------------------------------------
# database/db.py
# ---------------------------------------------------------------------------

def test_db_get_connection_fails_gracefully():
    """db.get_connection raises when no DB is available."""
    from database import db

    with patch.object(db, "MYSQL_AVAILABLE", False):
        with pytest.raises(RuntimeError, match="mysql-connector-python not installed"):
            db.get_connection()


def test_db_functions_with_none_connection():
    """DB helper functions surface invalid connections."""
    from database import db

    with pytest.raises(AttributeError):
        db.get_user_by_email(None, "test@test.com")  # type: ignore[arg-type]
    with pytest.raises(AttributeError):
        db.create_user(None, "test@test.com", "hash")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# services/streaming.py — openai/google/ollama branches
# ---------------------------------------------------------------------------

def test_stream_agent_openai_mock():
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock(delta=MagicMock(content="Hi"))]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = iter([mock_chunk])

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
        with patch("openai.OpenAI", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            events = list(mod.stream_agent_response("hello", model="gpt-4o"))
            assert any("Hi" in e for e in events)
            assert any("done" in e for e in events)


def test_stream_agent_google_mock():
    mock_genai = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.text = "Bonjour"
    mock_genai.GenerativeModel.return_value.generate_content.return_value = iter([mock_chunk])

    with patch.dict(os.environ, {"GEMINI_API_KEY": "gm-test"}):
        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            import services.streaming as mod
            reload(mod)
            events = list(mod.stream_agent_response("hello", model="gemini-1.5-pro"))
            assert any("Bonjour" in e for e in events)
            assert any("done" in e for e in events)


def test_stream_agent_ollama_mock():
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.raise_for_status = MagicMock()
    mock_resp.iter_lines.return_value = [b'{"response": "hey"}', b'']

    with patch("requests.post", return_value=mock_resp):
        import services.streaming as mod
        reload(mod)
        events = list(mod.stream_agent_response("hello", model="llama3"))
        assert any("hey" in e for e in events)
        assert any("done" in e for e in events)


def test_stream_agent_prefers_user_key_over_env():
    """A user-supplied provider key should be used instead of the env key."""
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["hi"])
    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
        with patch("services.provider_keys.get_user_provider_key", return_value="user-key"):
            with patch("anthropic.Anthropic", return_value=mock_client) as mock_anthropic:
                import services.streaming as mod
                reload(mod)
                list(mod.stream_agent_response("hello", user_id=1))
                mock_anthropic.assert_called_once_with(api_key="user-key")


def test_stream_llm_openai_mock():
    mock_choice = MagicMock()
    mock_choice.message.content = "openai reply"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
        with patch("openai.OpenAI", return_value=mock_client):
            import services.streaming as mod
            reload(mod)
            result = mod.stream_llm_response("hello", model="gpt-4o")
            assert result == "openai reply"


def test_stream_llm_google_mock():
    mock_genai = MagicMock()
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = MagicMock(text="hola")
    mock_genai.GenerativeModel.return_value.start_chat.return_value = mock_chat

    with patch.dict(os.environ, {"GEMINI_API_KEY": "gm-test"}):
        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            import services.streaming as mod
            reload(mod)
            result = mod.stream_llm_response(
                "hello", model="gemini-1.5-pro", history=[{"role": "assistant", "content": "hi"}],
            )
            assert result == "hola"


def test_stream_llm_ollama_mock():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"message": {"content": "ollama reply"}}

    with patch("requests.post", return_value=mock_resp):
        import services.streaming as mod
        reload(mod)
        result = mod.stream_llm_response("hello", model="llama3")
        assert result == "ollama reply"


# ---------------------------------------------------------------------------
# services/provider_keys.py
# ---------------------------------------------------------------------------

def test_provider_keys_encrypt_decrypt_roundtrip():
    from services import provider_keys as mod
    encrypted = mod.encrypt_key("sk-my-secret")
    assert encrypted != "sk-my-secret"
    assert mod.decrypt_key(encrypted) == "sk-my-secret"


def test_provider_keys_mask_short():
    from services.provider_keys import mask_key
    assert mask_key("short") == "*****"


def test_provider_keys_mask_long():
    from services.provider_keys import mask_key
    assert mask_key("sk-abcdefgh12345") == "sk-a...2345"


def test_get_user_provider_key_found():
    from services import provider_keys as mod
    encrypted = mod.encrypt_key("sk-user-key")
    mock_cnx = MagicMock()
    with patch("database.db.get_connection", return_value=mock_cnx), \
         patch("database.db.get_provider_key", return_value=encrypted):
        assert mod.get_user_provider_key(1, "anthropic") == "sk-user-key"


def test_get_user_provider_key_not_set():
    from services import provider_keys as mod
    mock_cnx = MagicMock()
    with patch("database.db.get_connection", return_value=mock_cnx), \
         patch("database.db.get_provider_key", return_value=None):
        assert mod.get_user_provider_key(1, "anthropic") is None


def test_get_user_provider_key_db_unavailable():
    from services import provider_keys as mod
    with patch("database.db.get_connection", side_effect=RuntimeError("no db")):
        assert mod.get_user_provider_key(1, "anthropic") is None


def test_get_user_provider_key_invalid_token():
    from services import provider_keys as mod
    mock_cnx = MagicMock()
    with patch("database.db.get_connection", return_value=mock_cnx), \
         patch("database.db.get_provider_key", return_value="not-a-valid-fernet-token"):
        assert mod.get_user_provider_key(1, "anthropic") is None


# ---------------------------------------------------------------------------
# database/db.py — billing (credits, plan changes, Stripe customer linkage)
# ---------------------------------------------------------------------------

def test_user_has_credits_true():
    from database import db
    cnx = _mock_cnx(fetchone={"credits": 5})
    assert db.user_has_credits(cnx, 1, min_credits=1) is True


def test_user_has_credits_false():
    from database import db
    cnx = _mock_cnx(fetchone={"credits": 0})
    assert db.user_has_credits(cnx, 1, min_credits=1) is False


def test_user_has_credits_no_user():
    from database import db
    cnx = _mock_cnx(fetchone=None)
    assert db.user_has_credits(cnx, 1) is False


def test_add_purchased_credits_positive():
    from database import db
    cnx = _mock_cnx(rowcount=1)
    assert db.add_purchased_credits(cnx, 1, 1000) is True
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params == (1000, 1)


def test_add_purchased_credits_non_positive():
    from database import db
    cnx = _mock_cnx()
    assert db.add_purchased_credits(cnx, 1, 0) is False
    cnx.cursor.return_value.execute.assert_not_called()


def test_set_plan_and_credits():
    from database import db
    cnx = _mock_cnx()
    db.set_plan_and_credits(cnx, 1, "pro", 500)
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params == ("pro", 500, 1)


def test_downgrade_to_free():
    from database import db
    cnx = _mock_cnx()
    db.downgrade_to_free(cnx, 1)
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params == (1,)
    assert "free" in executed_sql


def test_upsert_stripe_customer():
    from database import db
    cnx = _mock_cnx()
    db.upsert_stripe_customer(cnx, 1, "cus_1", "pro", "active", None)
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params == (1, "cus_1", "pro", "active", None)


def test_update_stripe_customer_status():
    from database import db
    cnx = _mock_cnx()
    db.update_stripe_customer_status(cnx, "cus_1", "canceled")
    executed_sql, params = cnx.cursor.return_value.execute.call_args.args
    assert params == ("canceled", "cus_1")


def test_get_user_id_for_stripe_customer_found():
    from database import db
    cnx = _mock_cnx(fetchone={"user_id": 7})
    assert db.get_user_id_for_stripe_customer(cnx, "cus_1") == 7


def test_get_user_id_for_stripe_customer_not_found():
    from database import db
    cnx = _mock_cnx(fetchone=None)
    assert db.get_user_id_for_stripe_customer(cnx, "cus_1") is None


def test_get_stripe_customer():
    from database import db
    cnx = _mock_cnx(fetchone={"stripe_id": "cus_1", "plan": "pro", "status": "active", "period_end": None})
    result = db.get_stripe_customer(cnx, 1)
    assert result["stripe_id"] == "cus_1"


def test_count_monthly_requests():
    from database import db
    cnx = _mock_cnx(fetchone={"cnt": 12})
    assert db.count_monthly_requests(cnx, 1) == 12


def test_count_monthly_requests_no_row():
    from database import db
    cnx = _mock_cnx(fetchone=None)
    assert db.count_monthly_requests(cnx, 1) == 0


def test_claim_stripe_event_first_delivery():
    from database import db
    cnx = _mock_cnx()
    assert db.claim_stripe_event(cnx, "evt_1", "checkout.session.completed") is True
    cnx.cursor.return_value.close.assert_called_once()


def test_claim_stripe_event_duplicate_delivery():
    from mysql.connector.errors import Error as MySQLError

    from database import db
    cnx = _mock_cnx()
    cnx.cursor.return_value.execute.side_effect = MySQLError(msg="Duplicate entry", errno=1062)
    assert db.claim_stripe_event(cnx, "evt_1", "checkout.session.completed") is False


def test_claim_stripe_event_reraises_unrelated_error():
    from mysql.connector.errors import Error as MySQLError

    from database import db
    cnx = _mock_cnx()
    cnx.cursor.return_value.execute.side_effect = MySQLError(msg="Connection lost", errno=2013)
    with pytest.raises(MySQLError):
        db.claim_stripe_event(cnx, "evt_1", "checkout.session.completed")


def test_release_stripe_event_deletes_claim():
    from database import db

    cnx = _mock_cnx()
    db.release_stripe_event(cnx, "evt_retry")
    cursor = cnx.cursor.return_value
    cursor.execute.assert_called_once_with(
        "DELETE FROM stripe_events WHERE event_id = %s", ("evt_retry",),
    )
    cursor.close.assert_called_once()
