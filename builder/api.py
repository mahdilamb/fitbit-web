"""Abstract implementations and types for reading the schema."""

from typing import Annotated, Any, Literal, Mapping, Sequence, TypeAlias

import pydantic

Method: TypeAlias = Literal["get", "post", "put", "delete", "patch"]
HttpStatusCode: TypeAlias = Annotated[str, pydantic.constr(pattern=r"[1-5]\d{2}")]
Consumes: TypeAlias = Literal[
    "multipart/form-data", "application/json", "application/x-www-form-urlencoded"
]
Produces: TypeAlias = Literal["application/json", "application/x-www-form-urlencoded"]
ParameterType: TypeAlias = Literal["boolean", "integer", "string"]
ParameterFormat: TypeAlias = Literal["date", "time", "timestamp"]
ParameterLocation: TypeAlias = Literal[
    "query", "header", "path", "cookie", "formData", "body"
]


class Contact(pydantic.BaseModel):
    """Contact information."""

    name: str
    url: pydantic.AnyHttpUrl | None = None
    email: pydantic.EmailStr | None = None


class Licence(pydantic.BaseModel):
    """Licence information."""

    name: str
    identifier: str | None = None
    url: pydantic.AnyHttpUrl | None = None


class Info(pydantic.BaseModel):
    """Info."""

    title: str
    description: str | None = None
    summary: str | None = None
    version: str
    terms_of_service: pydantic.AnyHttpUrl | None = pydantic.Field(
        default=None, alias="termsOfService"
    )
    contact: Contact | None = None
    licence: Licence | None = None


class ExternalDocs(pydantic.BaseModel):
    """External docs information."""

    description: str | None = None
    url: pydantic.AnyHttpUrl


class Tag(pydantic.BaseModel):
    """Tag information."""

    name: str
    description: str
    external_docs: ExternalDocs = pydantic.Field(alias="externalDocs")


class Reference(pydantic.BaseModel):
    """Reference to another location in the model."""

    ref: str = pydantic.Field(alias="$ref")
    summary: str | None = None
    desription: str | None = None


class Parameters(pydantic.BaseModel):
    """Parameter information."""

    name: str
    in_: ParameterLocation = pydantic.Field(alias="in")
    description: str | None
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool = pydantic.Field(alias="allowEmptyValue", default=False)
    type: ParameterType | None = None
    format: ParameterFormat | Sequence[ParameterFormat] | None = None
    enum: Sequence[str] | None = None
    default: Any | None = None


class Discriminator(pydantic.BaseModel):
    """Discriminator information."""

    property_name: ExternalDocs | None = pydantic.Field(
        alias="propertyName", default=None
    )
    mapping: Mapping[str, str] | None = None


class XML(pydantic.BaseModel):
    """XML info."""

    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False


class Example(pydantic.BaseModel):
    """An example."""

    summary: str | None = None
    description: str | None = None
    value: Any | None = None
    external_value: str | None = pydantic.Field(alias="externalValue", default=None)


class Schema(pydantic.BaseModel):
    """Schema information."""

    discriminator: Discriminator | None = None
    xml: XML | None = None
    external_docs: ExternalDocs | None = pydantic.Field(
        alias="externalDocs", default=None
    )
    example: Any | None = None


class Header(pydantic.BaseModel):
    """Header information."""

    name: str
    description: str | None = None
    external_docs: ExternalDocs | None = pydantic.Field(
        alias="externalDocs", default=None
    )


class Encoding(pydantic.BaseModel):
    """Encoding information."""

    content_type: ExternalDocs | None = pydantic.Field(
        alias="contentType", default=None
    )
    headers: Mapping[str, Header | Reference] | None = None
    style: str | None = None
    explode: bool = False
    allow_reserved: bool = pydantic.Field(alias="allowReserved", default=False)


class MediaType(pydantic.BaseModel):
    """The info on the type of media."""

    schema_: Schema | None = pydantic.Field(alias="schema", default=None)
    example: Any | None = None
    examples: Mapping[str, Example | Reference] | None = None
    encoding: Mapping[str, Encoding] | None = None


class RequestBody(pydantic.BaseModel):
    """The body of a request."""

    description: str | None = None
    content: Mapping[str, MediaType]
    required: bool = False


class ServerVariable(pydantic.BaseModel):
    """Information of variables in a server."""

    enum: Sequence[str] | None = None
    default: str
    description: str | None = None


class Server(pydantic.BaseModel):
    """Server info."""

    url: pydantic.AnyUrl
    description: str | None = None
    variables: Mapping[str, ServerVariable] | None = None


class Link(pydantic.BaseModel):
    """Link info."""

    operation_ref: str | None = pydantic.Field(alias="operationRef", default=None)
    operation_id: str | None = pydantic.Field(alias="operationId", default=None)
    parameters: Mapping[str, Any] | None = None
    request_body: Any | None = pydantic.Field(alias="requestBody", default=None)
    description: str | None = None
    server: Server | None = None


class Response(pydantic.BaseModel):
    """Response model."""

    description: str
    headers: Mapping[str, Header | Reference] | None = None
    content: Mapping[str, MediaType] | None = None
    links: Mapping[str, Link | Reference] | None = None


class Callback(pydantic.BaseModel, extra="allow"):
    """Callback details."""

    ...


class SecurityRequirement(pydantic.BaseModel, extra="allow"):
    """Security requirement."""

    ...


class Operation(pydantic.BaseModel):
    """Details of an operation."""

    tags: Sequence[str] | None = None
    summary: str | None = None
    description: str | None = None
    external_docs: ExternalDocs | None = pydantic.Field(
        alias="externalDocs", default=None
    )
    consumes: Sequence[str] | None = None
    produces: Sequence[str] | None = None
    operation_id: str | None = pydantic.Field(alias="operationId", default=None)
    parameters: Sequence[Parameters | Reference] | None = None
    request_body: RequestBody | Reference | None = pydantic.Field(
        alias="requestBody", default=None
    )
    responses: Mapping[HttpStatusCode, Response] | None = None
    callbacks: Mapping[str, Callback | Reference] | None = None
    deprecated: bool = False
    security: Sequence[SecurityRequirement] | None = None
    servers: Sequence[Server] | None = None


class DefinitionProperty(pydantic.BaseModel):
    """Definition property."""

    type: str
    example: Any | None = None
    items: Reference | None = None


class Definition(pydantic.BaseModel):
    """Definition in the Fitbit model."""

    type: str
    properties: Mapping[str, DefinitionProperty] | None = None


class SecurityDefinition(pydantic.BaseModel):
    """Security definition API."""

    type: str
    authorization_url: pydantic.AnyHttpUrl | None = pydantic.Field(
        alias="authorizationUrl", default=None
    )
    flow: str | None = None
    scopes: Mapping[str, str] | None = None


class FitbitWebAPI(pydantic.BaseModel):
    """The root for the Web API."""

    swagger: str
    info: Info
    host: str
    tags: Sequence[Tag]
    schemes: Sequence[Literal["http", "https"]]
    paths: dict[str, dict[Method, Operation]]
    security_definitions: Mapping[str, SecurityDefinition] | None = pydantic.Field(
        alias="securityDefinitions", default=None
    )
    definitions: Mapping[str, Definition] | None = None
    external_docs: ExternalDocs | None = pydantic.Field(
        alias="externalDocs", default=None
    )
