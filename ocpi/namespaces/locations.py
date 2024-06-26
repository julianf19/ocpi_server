#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 18:26:15 2021

@author: maurer
"""

from __future__ import annotations

import logging

from flask_restx import Namespace, Resource

from ocpi.models import resp, respList, respEmpty
from ocpi.models.location import (
    EVSE,
    EVSEOptional,
    Connector,
    ConnectorOptional,
    Location,
    LocationOptional,
    add_models_to_location_namespace,
)
from ocpi.namespaces import (
    get_header_parser,
    make_response,
    pagination_parser,
    token_required,
)

locations_ns = Namespace(name="locations", validate=True)

add_models_to_location_namespace(locations_ns)
parser = get_header_parser(locations_ns)

log = logging.getLogger("ocpi")


def receiver():
    # keep in mind: https://stackoverflow.com/a/16569475
    # @locations_ns.route(
    #     "/<string:location_id>",
    #     "/<string:location_id>/<string:evse_uid>",
    #     "/<string:location_id>/<string:evse_uid>/<string:connector_id>",
    # )
    # @locations_ns.expect(parser)
    # class get_location(Resource):
    #     def __init__(self, api=None, *args, **kwargs):
    #         self.locationmanager = kwargs["locations"]
    #         super().__init__(api, *args, **kwargs)

    #     @locations_ns.marshal_with(resp(locations_ns, Location))
    #     def get(self, location_id, evse_uid=None, connector_id=None):
    #         """
    #         Filter Locations/EVSEs/Connectors by id
    #         """

    #         return make_response(self.locationmanager.getLocation, "", "", location_id)

    # Receiver interface: eMSP and NSP.

    @locations_ns.route("/<string:country_code>/<string:party_id>/<string:location_id>")
    @locations_ns.expect(parser)
    class manage_location(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.locationmanager = kwargs["locations"]
            super().__init__(api, *args, **kwargs)

        @token_required
        @locations_ns.marshal_with(resp(locations_ns, Location))
        def get(self, country_code, party_id, location_id):
            """
            Get Location by ID
            """

            return make_response(
                self.locationmanager.getLocation, country_code, party_id, location_id
            )

        @token_required
        @locations_ns.expect(Location)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def put(self, country_code, party_id, location_id):
            """
            Add/Replace Location by ID
            """

            return make_response(
                self.locationmanager.putLocation,
                country_code,
                party_id,
                location_id,
                locations_ns.payload,
            )

        @token_required
        @locations_ns.expect(LocationOptional)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def patch(self, country_code, party_id, location_id):
            """
            Partially update Location
            """

            return make_response(
                self.locationmanager.patchLocation,
                country_code,
                party_id,
                location_id,
                locations_ns.payload,
            )
        
    @token_required
    @locations_ns.route(
        "/<string:country_code>/<string:party_id>/<string:location_id>/<string:evse_uid>"
    )
    @locations_ns.expect(parser)
    class manage_evse(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.locationmanager = kwargs["locations"]
            super().__init__(api, *args, **kwargs)

        @locations_ns.marshal_with(resp(locations_ns, EVSE))
        def get(self, country_code, party_id, location_id, evse_uid):
            """
            Get EVSE by ID
            """

            return make_response(
                self.locationmanager.getEVSE,
                country_code,
                party_id,
                location_id,
                evse_uid,
            )

        @token_required
        @locations_ns.expect(EVSE)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def put(self, country_code, party_id, location_id, evse_uid):
            """
            Add/Replace EVSE by ID
            """

            return make_response(
                self.locationmanager.putEVSE,
                country_code,
                party_id,
                location_id,
                evse_uid,
                locations_ns.payload,
            )

        @token_required
        @locations_ns.expect(EVSEOptional)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def patch(self, country_code, party_id, location_id, evse_uid):
            """
            Partially update EVSE
            """

            return make_response(
                self.locationmanager.patchEVSE,
                country_code,
                party_id,
                location_id,
                evse_uid,
                locations_ns.payload,
            )

    @token_required
    @locations_ns.route(
        "/<string:country_code>/<string:party_id>/<string:location_id>/<string:evse_uid>/<string:connector_id>"
    )
    @locations_ns.expect(parser)
    class manage_connector(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.locationmanager = kwargs["locations"]
            super().__init__(api, *args, **kwargs)

        @locations_ns.marshal_with(resp(locations_ns, Connector))
        def get(self, country_code, party_id, location_id, evse_uid, connector_id):
            """
            Get Connector by ID
            """

            return make_response(
                self.locationmanager.getConnector,
                country_code,
                party_id,
                location_id,
                evse_uid,
                connector_id,
            )

        @token_required
        @locations_ns.expect(Connector)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def put(self, country_code, party_id, location_id, evse_uid, connector_id):
            """
            Add/Replace Connector by ID
            """

            return make_response(
                self.locationmanager.putConnector,
                country_code,
                party_id,
                location_id,
                evse_uid,
                connector_id,
                locations_ns.payload,
            )
        
        @token_required
        @locations_ns.expect(ConnectorOptional)
        @locations_ns.marshal_with(respEmpty(locations_ns))
        def patch(self, country_code, party_id, location_id, evse_uid, connector_id):
            """
            Partially update Connector
            """

            return make_response(
                self.locationmanager.patchConnector,
                country_code,
                party_id,
                location_id,
                evse_uid,
                connector_id,
                locations_ns.payload,
            )

    return locations_ns


def sender():
    @locations_ns.route(
        "/", doc={"description": "API Endpoint for Locations management"}
    )
    @locations_ns.expect(parser)
    class get_locations(Resource):
        def __init__(self, api=None, *args, **kwargs):
            self.locationmanager = kwargs["locations"]
            super().__init__(api, *args, **kwargs)

        @locations_ns.doc(
            params={
                "from": {
                    "in": "query",
                    "description": "declare location last update",
                    "default": "2021-01-01T13:30:00+02:00",
                    "required": True,
                },
                "to": {
                    "in": "query",
                    "description": "declare location last update",
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
        @locations_ns.marshal_with(respList(locations_ns, Location))
        @token_required
        @locations_ns.header("Link", "Link to the next ressource")
        @locations_ns.header(
            "X-Total-Count",
            "Count of available Ressources with respect to filter but ignoring paginatino",
        )
        @locations_ns.header(
            "X-Limit", "The maximum number of objects that the server can return."
        )
        def get(self):
            """
            Get Locations, allows pagination
            """
            parser = pagination_parser()
            args = parser.parse_args()

            return make_response(
                self.locationmanager.getLocations,
                args["from"],
                args["to"],
                args["offset"],
                args["limit"],
            )
            # TODO Link Header must contain a full url, which is quite bad abstraction-wise
            # as the url should not be known to the managers


def makeLocationNamespace(role):
    if role == "SENDER":
        sender()
    elif role == "RECEIVER":
        receiver()
    else:
        raise Exception("invalid role")
    return locations_ns