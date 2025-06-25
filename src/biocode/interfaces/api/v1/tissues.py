"""Tissue API Endpoints"""
from typing import List
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/")
async def list_tissues():
    """List all tissues"""
    return {"message": "Tissue endpoints coming soon", "tissues": []}


@router.post("/")
async def create_tissue():
    """Create a new tissue"""
    return {"message": "Tissue creation coming soon"}


@router.get("/{tissue_id}")
async def get_tissue(tissue_id: str):
    """Get a specific tissue"""
    return {"message": f"Tissue {tissue_id} details coming soon"}