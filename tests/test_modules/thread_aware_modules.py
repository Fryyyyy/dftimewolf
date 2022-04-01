# -*- coding: utf-8 -*-
"""Contains dummy modules used in thread aware tests."""

from typing import Dict, Any
import threading
import time

from dftimewolf.lib import module
from dftimewolf.lib.containers import interface
from dftimewolf.lib.containers import containers


class TestContainer(interface.AttributeContainer):
  """Test attribute container."""

  CONTAINER_TYPE = 'test_container'

  def __init__(self, value: str) -> None:
    super(TestContainer, self).__init__()
    self.value = value

  def __eq__(self, other: object) -> bool:
    return self.value == other.value

class TestContainerTwo(interface.AttributeContainer):
  """Test attribute container."""

  CONTAINER_TYPE = 'test_container_two'

  def __init__(self, value: str) -> None:
    super(TestContainerTwo, self).__init__()
    self.value = value

class TestContainerThree(interface.AttributeContainer):
  """Test attribute container."""

  CONTAINER_TYPE = 'test_container_three'

  def __init__(self, value: str) -> None:
    super(TestContainerThree, self).__init__()
    self.value = value


class ContainerGeneratorModule(module.BaseModule):
  """This is a dummy module. Generates test containers."""

  def __init__(self, state, name=None):
    self.list = []
    super(ContainerGeneratorModule, self).__init__(state, name)

  def SetUp(self, runtime_value=None): # pylint: disable=arguments-differ
    """Dummy setup function."""
    print(self.name + ' Setup!')
    self.list = runtime_value.split(',')

  def Process(self):
    """Dummy Process function."""
    print(self.name + ' Process!')
    for item in self.list:
      container = TestContainer(item)
      self.state.StoreContainer(container)
    container = TestContainerTwo(','.join(self.list))
    self.state.StoreContainer(container)

class ThreadAwareConsumerModule(module.ThreadAwareModule):
  """This is a dummy Thread Aware Module. Consumes from
  ContainerGeneratorModule based on the number of containers generated."""

  def __init__(self, state, name=None):
    super(ThreadAwareConsumerModule, self).__init__(state, name)
    self.output_values = ['one', 'two', 'three']
    self.output_lock = threading.Lock()

  def SetUp(self): # pylint: disable=arguments-differ
    """SetUp"""
    self.logger.info('{0:s} SetUp!'.format(self.name))

  def Process(self, container) -> None:
    """Process"""
    self.logger.info('{0:s} Process!'.format(self.name))

    time.sleep(1)

    # This modifies the container passed in as a parameter.
    container.value += ' appended'

    # This modifies some state-stored containers, generated by previous modules.
    for c in self.state.GetContainers(TestContainerTwo):
      c.value += ' appended'

    # This generates and stores a container in state.
    with self.output_lock:
      new_container = TestContainerThree('output ' + self.output_values.pop())
    self.state.StoreContainer(new_container)

  @staticmethod
  def GetThreadOnContainerType():
    return TestContainer

  def GetThreadPoolSize(self):
    return 2

  def PreProcess(self) -> None:
    self.logger.info("ThreadAwareConsumerModule Static Pre Process")

  def PostProcess(self) -> None:
    self.logger.info("ThreadAwareConsumerModule Static Post Process")

class Issue503Module(module.ThreadAwareModule):
  """This is a module for testing a certain pattern of container handling.

  As described by https://github.com/log2timeline/dftimewolf/issues/503 this
  module pops containers for input, and uses the same container type as output.
  """
  def __init__(self, state, name=None):
    super(Issue503Module, self).__init__(state, name)

  def SetUp(self): # pylint: disable=arguments-differ
    """SetUp"""
    self.logger.info('{0:s} SetUp!'.format(self.name))

  def Process(self, container) -> None:
    """Process"""
    self.logger.info('{0:s} Process!'.format(self.name))
    self.state.StoreContainer(TestContainer(container.value + " Processed"))

  @staticmethod
  def GetThreadOnContainerType():
    return TestContainer

  def GetThreadPoolSize(self):
    return 2

  def PreProcess(self) -> None:
    pass

  def PostProcess(self) -> None:
    pass

  def KeepThreadedContainersInState(self) -> bool:  # pylint: disable=arguments-differ
    return False
