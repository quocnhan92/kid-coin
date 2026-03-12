from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditStatus
from app.core import context
from typing import Optional, Dict, Any
import json
import traceback

class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        duration_ms: Optional[int] = None
    ):
        """
        Creates an audit log entry.
        Automatically uses context.get_request_id() if request_id is not provided.
        """
        
        # Auto-fetch request_id from context
        final_request_id = request_id or context.get_request_id()
        final_user_id = user_id or context.get_current_user_id()

        log_entry = AuditLog(
            user_id=final_user_id,
            action=action,
            status=status,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=final_request_id,
            duration_ms=duration_ms
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def log_failed(
        db: Session,
        action: str,
        resource_type: str,
        error: Exception,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Helper to log a failed action.
        """
        error_msg = f"{str(error)}\n{traceback.format_exc()}"
        return AuditService.log(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=AuditStatus.FAILED,
            details=details,
            error_message=error_msg,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id
        )
