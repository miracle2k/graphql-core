# flake8: noqa
from graphql.core.error import format_error
from graphql.core.execution import Executor
from graphql.core.execution.middlewares.gevent import GeventExecutionMiddleware, run_in_greenlet
from graphql.core.language.location import SourceLocation
from graphql.core.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLString
)

import gevent


def test_gevent_executor():
    doc = 'query Example { a, b }'

    @run_in_greenlet
    def resolver(context, *_):
        gevent.sleep(0.001)
        return 'hey'

    @run_in_greenlet
    def resolver_2(context, *_):
        gevent.sleep(0.003)
        return 'hey2'

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2)
    })

    executor = Executor([GeventExecutionMiddleware()])
    result = executor.execute(GraphQLSchema(Type), doc)
    assert not result.errors
    assert result.data == {'a': 'hey', 'b': 'hey2'}


def test_gevent_executor_with_error():
    doc = 'query Example { a, b }'

    @run_in_greenlet
    def resolver(context, *_):
        gevent.sleep(0.001)
        return 'hey'

    @run_in_greenlet
    def resolver_2(context, *_):
        gevent.sleep(0.003)
        raise Exception('resolver_2 failed!')

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2)
    })

    executor = Executor([GeventExecutionMiddleware()])
    result = executor.execute(GraphQLSchema(Type), doc)
    formatted_errors = list(map(format_error, result.errors))
    assert formatted_errors == [{'locations': [{'line': 1, 'column': 20}], 'message': 'resolver_2 failed!'}]
    assert result.data == {'a': 'hey', 'b': None}
