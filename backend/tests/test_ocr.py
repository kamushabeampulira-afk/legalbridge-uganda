"""Tests: OCR text extraction and document classification."""
import pytest
from documents.ocr import (
    classify_document_type,
    extract_key_fields,
    _extract_dates,
    _extract_amounts,
    _extract_references,
)


def test_classify_traffic_notice():
    text = (
        "TRAFFIC VIOLATION NOTICE\n"
        "Vehicle: UBA 123Z\n"
        "Alleged offence: Driving without a licence\n"
        "Road Safety Officer: P. Opio, Badge 4521\n"
        "Penalty: UGX 50,000"
    )
    assert classify_document_type(text) == 'traffic_notice'


def test_classify_eviction_notice():
    text = (
        "NOTICE TO VACATE\n"
        "To: Jane Nakato, Stall 14B\n"
        "You are hereby required to vacate the market stall\n"
        "within 14 days from the date of this notice."
    )
    assert classify_document_type(text) == 'eviction_notice'


def test_classify_allocation_slip():
    text = (
        "MARKET STALL ALLOCATION SLIP\n"
        "This is to certify that John Mukasa has been allocated\n"
        "trading space No. 22A at Nakasero Market.\n"
        "Allocated by: Market Manager"
    )
    assert classify_document_type(text) == 'allocation_slip'


def test_classify_payment_receipt():
    text = (
        "OFFICIAL PAYMENT RECEIPT\n"
        "Receipt No. 00445\n"
        "Amount paid: UGX 120,000\n"
        "Received from: Sarah Atim\n"
        "Payment received for market fees"
    )
    assert classify_document_type(text) == 'payment_receipt'


def test_classify_unknown():
    text = "Hello world, this text has no legal keywords at all."
    assert classify_document_type(text) == 'unknown'


def test_extract_ugx_amounts():
    text = "Fine: UGX 50,000 payable within 14 days. Total: Shs. 75,000"
    amounts = _extract_amounts(text)
    assert any('50,000' in a for a in amounts)


def test_extract_dates():
    text = "Issued on 15/06/2024. Deadline: 30 June 2024."
    dates = _extract_dates(text)
    assert len(dates) >= 1


def test_extract_reference_numbers():
    text = "Reference: TRF/2024/00123\nCase No. CR-456/2024"
    refs = _extract_references(text)
    assert any('TRF/2024/00123' in r or '00123' in r for r in refs)


def test_extract_key_fields_combined():
    text = (
        "Traffic Notice Ref TRF/001\n"
        "Date: 01/07/2024\n"
        "Penalty: UGX 30,000\n"
        "Officer: P. Opio"
    )
    fields = extract_key_fields(text)
    assert isinstance(fields['dates'], list)
    assert isinstance(fields['amounts'], list)
    assert isinstance(fields['reference_numbers'], list)
