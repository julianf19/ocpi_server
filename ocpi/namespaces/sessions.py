#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 12:32:01 2021

@author: maurer
"""

from __future__ import annotations

from flask_restx import Namespace, Resource, fields

from ocpi.models import resp, respList, respRaw, respEmpty
from ocpi.models.sessions import (
    Session,
    SessionOptional,
    add_models_to_session_namespace,
)
from ocpi.namespaces import (
    get_header_parser,
    make_response,
    pagination_parser,
    token_required,
)

sessions_ns = Namespace(name="sessions", validate=True)
add_models_to_session_namespace(sessions_ns)
header_parser = get_header_parser(sessions_ns)

def sender():
    @sessions_ns.route("/", doc={"description": "API Endpoint for Session management"})
    @sessions_ns.expect(header_parser)
    class get_sessions(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.sessionmanager = kwargs["sessions"]
            super().__init__(api, *args, **kwargs)

        @sessions_ns.doc(
            params={
                "from": {
                    "in": "query",
                    "description": "declare session start point",
                    "default": "2021-01-01T13:30:00+02:00",
                    "required": True,
                },
                "to": {
                    "in": "query",
                    "description": "declare session end point",
                    "default": "2038-01-01T15:30:00+02:00",
                    "required": True,
                },
                "offset": {
                    "in": "query",
                    "description": "id offset for pagination",
                    "default": "0",
                },
                "limit": {
                    "in": "query",
                    "description": "number of entries to get",
                    "default": "50",
                },
            }
        )
        @sessions_ns.marshal_with(respList(sessions_ns, Session))
        @token_required
        def get(self):
            """
            Only Sessions with last_update between the given {date_from} (including) and {date_to} (excluding) will be returned.
            """
            parser = pagination_parser()
            args = parser.parse_args()
            return make_response(
                self.sessionmanager.getSessions,
                args["from"],
                args["to"],
                args["offset"],
                args["limit"],
            )

    return sessions_ns


def receiver():
    @sessions_ns.route(
        "/<string:country_id>/<string:party_id>/<string:session_id>",
        doc={"description": "API Endpoint for Session management"},
    )
    @sessions_ns.response(404, "Command not found")
    @sessions_ns.expect(header_parser)
    class receiver_session(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.session_manager = kwargs["sessions"]
            super().__init__(api, *args, **kwargs)

        @sessions_ns.marshal_with(resp(sessions_ns, Session), code=200)
        @token_required
        def get(self, country_id, party_id, session_id):
            return make_response(
                self.session_manager.getSession, country_id, party_id, session_id
            )

        @sessions_ns.expect(Session)
        @sessions_ns.marshal_with(respEmpty(sessions_ns), code=201)
        @token_required
        def put(self, country_id, party_id, session_id):
            """Add new Session"""
            session_id = session_id.upper()  # caseinsensitive
            country_id = country_id.upper()
            party_id = party_id.upper()

            return make_response(
                self.session_manager.createSession,
                country_id,
                party_id,
                sessions_ns.payload,
            )

        @sessions_ns.expect(Session, validate=False)
        @sessions_ns.marshal_with(respEmpty(sessions_ns), code=201)
        @token_required
        def patch(self, country_id, party_id, session_id):
            session_id = session_id.upper()  # caseinsensitive
            country_id = country_id.upper()
            party_id = party_id.upper()

            return make_response(
                self.session_manager.patchSession,
                country_id,
                party_id,
                session_id,
                sessions_ns.payload,
            )

    return sessions_ns


def makeSessionNamespace(role):
    if role == "SENDER":
        sender()
    elif role == "RECEIVER":
        receiver()
    else:
        raise Exception("invalid role")

    return sessions_ns
