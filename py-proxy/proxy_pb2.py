# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proxy.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='proxy.proto',
  package='',
  syntax='proto3',
  serialized_pb=b'\n\x0bproxy.proto\"\x15\n\x05Strip\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"\x1e\n\x0c\x42lockRequest\x12\x0e\n\x06\x62locks\x18\x01 \x01(\r\"$\n\nBlockReply\x12\x16\n\x06strips\x18\x01 \x03(\x0b\x32\x06.Strip28\n\x05Proxy\x12/\n\x0fGetRandomBlocks\x12\r.BlockRequest\x1a\x0b.BlockReply\"\x00\x42\x19\n\x17\x63h.unine.iiun.safecloudb\x06proto3'
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_STRIP = _descriptor.Descriptor(
  name='Strip',
  full_name='Strip',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='Strip.data', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=15,
  serialized_end=36,
)


_BLOCKREQUEST = _descriptor.Descriptor(
  name='BlockRequest',
  full_name='BlockRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blocks', full_name='BlockRequest.blocks', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=68,
)


_BLOCKREPLY = _descriptor.Descriptor(
  name='BlockReply',
  full_name='BlockReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='strips', full_name='BlockReply.strips', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=106,
)

_BLOCKREPLY.fields_by_name['strips'].message_type = _STRIP
DESCRIPTOR.message_types_by_name['Strip'] = _STRIP
DESCRIPTOR.message_types_by_name['BlockRequest'] = _BLOCKREQUEST
DESCRIPTOR.message_types_by_name['BlockReply'] = _BLOCKREPLY

Strip = _reflection.GeneratedProtocolMessageType('Strip', (_message.Message,), dict(
  DESCRIPTOR = _STRIP,
  __module__ = 'proxy_pb2'
  # @@protoc_insertion_point(class_scope:Strip)
  ))
_sym_db.RegisterMessage(Strip)

BlockRequest = _reflection.GeneratedProtocolMessageType('BlockRequest', (_message.Message,), dict(
  DESCRIPTOR = _BLOCKREQUEST,
  __module__ = 'proxy_pb2'
  # @@protoc_insertion_point(class_scope:BlockRequest)
  ))
_sym_db.RegisterMessage(BlockRequest)

BlockReply = _reflection.GeneratedProtocolMessageType('BlockReply', (_message.Message,), dict(
  DESCRIPTOR = _BLOCKREPLY,
  __module__ = 'proxy_pb2'
  # @@protoc_insertion_point(class_scope:BlockReply)
  ))
_sym_db.RegisterMessage(BlockReply)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), b'\n\027ch.unine.iiun.safecloud')
# @@protoc_insertion_point(module_scope)
