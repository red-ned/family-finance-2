from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import Integ
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)



class _Base(DeclarativeBase):
    pass


class AccountType(_Base):
    __tablename__ = 'account_type'

    id             = mapped_column("id", Integer,
                                   primary_key=True)
    name           = mapped_column("name", String,
                                   unique=True)


class AccountLine(_Base):
    __tablename__ = 'account_line'

    id             = mapped_column("id", Integer,
                                   primary_key=True)
    transaction_id = mapped_column("transaction_id", Integer)
    date           = mapped_column("date", DateTime)
    line_type_id   = mapped_column("line_type_id", Integer)
    account_id     = mapped_column("account_id", Integer)
    description    = mapped_column("description", String)
    confirmation   = mapped_column("confirmation", String)
    complete_id    = mapped_column("complete_id", Integer)
    amount         = mapped_column("amount", Integer)
    credit_debit   = mapped_column("credit_debit", Boolean)

    name: Mapped[str]



class Account(_Base):
    __tablename__ = 'account'

    id              = mapped_column("id", Integer,
                                   primary_key=True)
    name            = mapped_column("name", String,
                                   unique=True)
    account_type_id = mapped_column("account_type_id", Integer)
    closed          = mapped_column("date", Boolean)
    credit_debit    = mapped_column("credit_debit", Boolean)
    envelopes       = mapped_column("envelopes", Boolean)