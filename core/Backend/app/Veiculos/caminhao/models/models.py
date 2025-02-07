from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean
from sqlalchemy.sql import func
from app.database.database import Base



class Caminhao(Base):
    __tablename__ = "veiculos_pesados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    marca = Column(String, index=True, doc="Marca do veiculo")
    modelo = Column(String, index=True, doc="Modelo do veiculo")
    ano = Column(Integer, index=True, doc="Ano do veiculo")
    preco = Column(Integer, index=True, doc="Preco do veiculo")
    tipo = Column(String, index=True, doc="Tipo do veiculo")
    cap_maxima = Column(Integer, index=True, doc="Capacidade maxima do veiculo")
    disponivel = Column(Boolean, index=True, doc="Disponibilidade do veiculo")
    quilometragem = Column(Float, index=True, doc="Kilometragem do veiculo")
    cor = Column(String, index=True, doc="Cor do veiculo")
    portas = Column(Integer, index=True, doc="Numero de portas do veiculo")
    lugares = Column(Integer, index=True, doc="Quantidade de lugares do veiculo")
    combustivel = Column(String, index=True, doc="Combustivel do veiculo")
    descricao = Column(String, doc="Descricao do veiculo")
    endereco = Column(String, doc="Endereco do usuario")
    imagem = Column(String, doc="Imagem do veiculo", info="Imagem do veiculo")
    data_cadastro = Column(DateTime, server_default=func.now(), doc="Data e hora do cadastro do veículo")

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