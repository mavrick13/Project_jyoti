from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class ChatGroup(Base):
    __tablename__ = "chat_groups"

    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class ChatGroupMember(Base):
    __tablename__ = "chat_group_members"

    member_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("chat_groups.group_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # Relationships
    group = relationship("ChatGroup", foreign_keys=[group_id])
    user = relationship("User", foreign_keys=[user_id])


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("chat_groups.group_id"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, file, etc.
    file_url = Column(String(500), nullable=True)
    reply_to_message_id = Column(Integer, ForeignKey("messages.message_id"), nullable=True)
    mentions = Column(Text, nullable=True)  # JSON string of mentioned user IDs
    tags = Column(Text, nullable=True)  # JSON string of tags
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=True)
    farmer_beneficiary_id = Column(String(50), ForeignKey("farmers.beneficiary_id"), nullable=True)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship("ChatGroup", foreign_keys=[group_id])
    sender = relationship("User", foreign_keys=[sender_user_id])
    reply_to = relationship("Message", foreign_keys=[reply_to_message_id], remote_side=[message_id])
    task = relationship("Task", foreign_keys=[task_id])
    farmer = relationship("Farmer", foreign_keys=[farmer_beneficiary_id])