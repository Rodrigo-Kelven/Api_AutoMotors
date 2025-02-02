# app/models/models.py
from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

# criar um modelo para cada categoria


# tabela que será criada no db
class Carro(Base):
    __tablename__ = "carros"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    modelo = Column(String, index=True, doc="Modelo do veiculo")
    ano = Column(Integer, index=True, doc="Ano do veiculo")
    kilometros = Column(Float, index=True, doc="Kilometragem do veiculo")
    cor = Column(String, index=True, doc="Cor do veiculo")
    combustivel = Column(String, index=True, doc="Combustivel do veiculo")
    preco = Column(Integer, index=True, doc="Preco do veiculo")
    descricao = Column(String, doc="Descricao do veiculo")
    imagem = Column(String, doc="Imagem do veiculo", info="Imagem do veiculo")


"""
class Column(
    __name_pos: str | type[TypeEngine[str]] | TypeEngine[str] | SchemaEventTarget | None = None,
    __type_pos: type[TypeEngine[str]] | TypeEngine[str] | SchemaEventTarget | None = None,
    *args: SchemaEventTarget,
    name: str | None = None,
    type_: type[TypeEngine[str]] | TypeEngine[str] | None = None,
    autoincrement: _AutoIncrementType = "auto",
    default: Any | None = _NoArg.NO_ARG,
    insert_default: Any | None = _NoArg.NO_ARG,
    doc: str | None = None,
    key: str | None = None,
    index: bool | None = None,
    unique: bool | None = None,
    info: _InfoType | None = None,
    nullable: bool | Literal[SchemaConst.NULL_UNSPECIFIED] | None = SchemaConst.NULL_UNSPECIFIED,
    onupdate: Any | None = None,
    primary_key: bool = False,
    server_default: _ServerDefaultArgument | None = None,
    server_onupdate: _ServerOnUpdateArgument | None = None,
    quote: bool | None = None,
    system: bool = False,
    comment: str | None = None,
    insert_sentinel: bool = False,
    _omit_from_statements: bool = False,
    _proxies: Any | None = None,
    **dialect_kwargs: Any
)
"""