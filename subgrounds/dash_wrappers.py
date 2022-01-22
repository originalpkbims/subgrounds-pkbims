from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, ClassVar
from pipe import traverse, where, map

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output

from subgrounds.plotly_wrappers import Figure
from subgrounds.subgraph import FieldPath
from subgrounds.subgrounds import Subgrounds, to_dataframe


class Refreshable(ABC):
  @property
  @abstractmethod
  def dash_dependencies(self) -> list[Output]:
    raise NotImplementedError

  @property
  @abstractmethod
  def dash_dependencies_outputs(self) -> list[Any]:
    raise NotImplementedError


class Graph(dcc.Graph, Refreshable):
  counter: ClassVar[int] = 0
  wrapped_figure: Figure

  def __init__(self, fig: Figure, **kwargs) -> None:
    super().__init__(id=f'graph-{Graph.counter}', figure=fig.figure, **kwargs)
    Graph.counter += 1
    self.wrapped_figure = fig

  @property
  def dash_dependencies(self) -> list[Output]:
    return [Output(self.id, 'figure')]

  @property
  def dash_dependencies_outputs(self) -> list[Any]:
    self.wrapped_figure.refresh()
    return [self.wrapped_figure.figure]


class DataTable(dash_table.DataTable, Refreshable):
  counter: ClassVar[int] = 0

  def __init__(self, subgrounds: Subgrounds, columns: FieldPath | list[FieldPath], **kwargs):
    self.subgrounds = subgrounds
    self.req = self.subgrounds.mk_request(list([columns] | traverse))

    super().__init__(id=f'datatable-{DataTable.counter}', **kwargs)
    DataTable.counter += 1

    self.refresh()

  def refresh(self) -> None:
    self.df = to_dataframe(self.subgrounds.execute(self.req))
    self.columns = [{"name": i, "id": i} for i in self.df.columns]
    self.data = self.df.to_dict('records')

  @property
  def dash_dependencies(self) -> list[Output]:
    return [Output(self.id, 'data')]

  @property
  def dash_dependencies_outputs(self) -> list[Output]:
    self.refresh()
    return [self.df.to_dict('records')]


class AutoUpdate(html.Div):
  counter: ClassVar[int] = 0

  def __init__(self, app, sec_interval: int = 1, children=[], **kwargs):
    id = f'interval-{AutoUpdate.counter}'
    
    super().__init__(
      children=[dcc.Interval(id=id, interval=sec_interval * 1000, n_intervals=0), *children],
      **kwargs
    )

    AutoUpdate.counter += 1

    def flatten(l):
      return [item for sublist in l for item in sublist]

    subgrounds_children = list(children | where(lambda child: isinstance(child, Refreshable)))
    deps = flatten(list(subgrounds_children | map(lambda child: child.dash_dependencies)))

    def update(n):
      outputs = flatten(list(subgrounds_children | map(lambda child: child.dash_dependencies_outputs)))

      if len(outputs) == 1:
        return outputs[0]
      else:
        return outputs

    # Register callback
    app.callback(*deps, Input(id, 'n_intervals'))(update)
