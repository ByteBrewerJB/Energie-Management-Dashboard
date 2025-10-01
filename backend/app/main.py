from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .api.router import api_router
from .core.config import settings
from .core.deps import authenticate_user, get_db_session, get_user_by_email
from .core.security import create_access_token, get_password_hash
from .db.init_db import init_db
from .models.assets import Battery, SolarPanelInstallation
from .models.car import Car
from .models.car_charge_journal import CarChargeJournal
from .models.monthly_journal import MonthlyJournal
from .models.user import User
from .schemas.user import UserCreate
from .services.dashboard import get_dashboard_data
from .services.roi import calculate_roi

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title=settings.project_name, debug=settings.debug)
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    value = value.strip().replace(",", ".")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ongeldige numerieke waarde: {value}")



def _safe_date(value: Optional[str]) -> Optional[date]:
    if value is None or value.strip() == "":
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Onjuiste datum: {value}")

def _get_user_from_token(db: Session, token: Optional[str]) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        if not sub:
            return None
        return db.get(User, int(sub))
    except (JWTError, ValueError):
        return None


def _require_user(request: Request, db: Session) -> User:
    token = request.cookies.get("access_token")
    user = _get_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail="redirect")
    return user


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_303_SEE_OTHER and exc.detail == "redirect":
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    raise exc


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": request.query_params.get("error")})


@app.post("/login", include_in_schema=False)
async def login_action(
    request: Request,
    db: Session = Depends(get_db_session),
):
    form = await request.form()
    email = form.get("email", "")
    password = form.get("password", "")
    user = authenticate_user(db, email, password)
    if not user:
        return RedirectResponse("/login?error=Ongeldige+inlog", status_code=status.HTTP_303_SEE_OTHER)
    token = create_access_token(user.id)
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=settings.access_token_expires_minutes * 60,
    )
    return response


@app.get("/logout", include_in_schema=False)
async def logout_action():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": request.query_params.get("error")})


@app.post("/register", include_in_schema=False)
async def register_action(
    request: Request,
    db: Session = Depends(get_db_session),
):
    form = await request.form()
    email = form.get("email")
    full_name = form.get("full_name")
    password = form.get("password")
    confirm_password = form.get("confirm_password")

    if not email or not password or password != confirm_password:
        return RedirectResponse("/register?error=Controleer+je+invoer", status_code=status.HTTP_303_SEE_OTHER)

    if get_user_by_email(db, email):
        return RedirectResponse("/register?error=E-mailadres+bestaat+al", status_code=status.HTTP_303_SEE_OTHER)

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        is_active=True,
    )
    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", include_in_schema=False)
async def dashboard_view(
    request: Request,
    year: Optional[int] = None,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    available_years = [
        row[0]
        for row in db.query(MonthlyJournal.year)
        .filter(MonthlyJournal.owner_id == user.id)
        .distinct()
        .order_by(MonthlyJournal.year.desc())
    ]
    selected_year = year or (available_years[0] if available_years else datetime.utcnow().year)

    dashboard_data = get_dashboard_data(db, user.id, selected_year)
    roi_progress = calculate_roi(db, user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "selected_year": selected_year,
            "available_years": available_years,
            "dashboard": dashboard_data,
            "roi": roi_progress,
        },
    )


@app.get("/journals", include_in_schema=False)
async def journals_view(
    request: Request,
    journal_id: Optional[int] = None,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    journals = (
        db.query(MonthlyJournal)
        .filter(MonthlyJournal.owner_id == user.id)
        .order_by(MonthlyJournal.year.desc(), MonthlyJournal.month.desc())
        .all()
    )
    cars = (
        db.query(Car)
        .filter(Car.owner_id == user.id, Car.is_active.is_(True))
        .order_by(Car.name.asc())
        .all()
    )
    journal_to_edit = None
    car_charge_map: Dict[int, float] = {}
    if journal_id:
        journal_to_edit = db.query(MonthlyJournal).filter(
            MonthlyJournal.id == journal_id, MonthlyJournal.owner_id == user.id
        ).first()
        if journal_to_edit:
            car_charge_map = {charge.car_id: charge.charged_kwh for charge in journal_to_edit.car_charges}

    return templates.TemplateResponse(
        "journal_form.html",
        {
            "request": request,
            "user": user,
            "journals": journals,
            "cars": cars,
            "journal": journal_to_edit,
            "car_charge_map": car_charge_map,
            "message": request.query_params.get("message"),
        },
    )


@app.post("/journals/save", include_in_schema=False)
async def journals_save(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    form = await request.form()
    journal_id = form.get("journal_id")
    year = int(form.get("year"))
    month = int(form.get("month"))

    fields = {
        "consumption_tariff_1_kwh": _safe_float(form.get("consumption_tariff_1_kwh")),
        "consumption_tariff_2_kwh": _safe_float(form.get("consumption_tariff_2_kwh")),
        "feed_in_without_battery_kwh": _safe_float(form.get("feed_in_without_battery_kwh")),
        "total_house_consumption_kwh": _safe_float(form.get("total_house_consumption_kwh")),
        "avg_consumption_tariff_low_eur_kwh": _safe_float(form.get("avg_consumption_tariff_low_eur_kwh")),
        "avg_consumption_tariff_high_eur_kwh": _safe_float(form.get("avg_consumption_tariff_high_eur_kwh")),
        "supplier_costs_eur": _safe_float(form.get("supplier_costs_eur")),
        "avg_feed_in_tariff_eur_kwh": _safe_float(form.get("avg_feed_in_tariff_eur_kwh")),
        "solar_production_kwh": _safe_float(form.get("solar_production_kwh")),
        "battery_charge_kwh": _safe_float(form.get("battery_charge_kwh")),
        "battery_discharge_kwh": _safe_float(form.get("battery_discharge_kwh")),
        "advance_payment_eur": _safe_float(form.get("advance_payment_eur")),
    }

    cars = db.query(Car).filter(Car.owner_id == user.id).all()
    charges = []
    for car in cars:
        value = _safe_float(form.get(f"car_{car.id}_charged_kwh"))
        if value is not None:
            charges.append((car.id, value))

    if journal_id:
        journal = db.query(MonthlyJournal).filter(
            MonthlyJournal.id == int(journal_id), MonthlyJournal.owner_id == user.id
        ).first()
        if not journal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journaal niet gevonden")
        journal.year = year
        journal.month = month
        for field, value in fields.items():
            setattr(journal, field, value)
        db.query(CarChargeJournal).filter(CarChargeJournal.journal_id == journal.id).delete()
    else:
        existing = db.query(MonthlyJournal).filter(
            MonthlyJournal.owner_id == user.id,
            MonthlyJournal.year == year,
            MonthlyJournal.month == month,
        ).first()
        if existing:
            return RedirectResponse(
                f"/journals?message=Journaal+voor+{month}-{year}+bestaat+al",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        journal = MonthlyJournal(owner_id=user.id, year=year, month=month, **fields)
        db.add(journal)
        db.flush()

    for car_id, charged_kwh in charges:
        db.add(CarChargeJournal(journal_id=journal.id, car_id=car_id, charged_kwh=charged_kwh))

    db.commit()
    return RedirectResponse("/journals?message=Journaal+opgeslagen", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/journals/{journal_id}/delete", include_in_schema=False)
async def journals_delete(
    journal_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    journal = db.query(MonthlyJournal).filter(
        MonthlyJournal.id == journal_id, MonthlyJournal.owner_id == user.id
    ).first()
    if journal:
        db.delete(journal)
        db.commit()
    return RedirectResponse("/journals?message=Journaal+verwijderd", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/assets", include_in_schema=False)
async def assets_view(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    solar = (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == user.id)
        .first()
    )
    battery = db.query(Battery).filter(Battery.owner_id == user.id).first()
    roi_progress = calculate_roi(db, user.id)

    return templates.TemplateResponse(
        "assets.html",
        {
            "request": request,
            "user": user,
            "solar": solar,
            "battery": battery,
            "roi": roi_progress,
            "message": request.query_params.get("message"),
        },
    )


@app.post("/assets/solar", include_in_schema=False)
async def assets_solar_save(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    form = await request.form()
    solar = (
        db.query(SolarPanelInstallation)
        .filter(SolarPanelInstallation.owner_id == user.id)
        .first()
    )
    if not solar:
        solar = SolarPanelInstallation(owner_id=user.id)
        db.add(solar)

    solar.purchase_date = _safe_date(form.get("purchase_date"))
    solar.purchase_cost_eur = _safe_float(form.get("purchase_cost_eur"))
    solar.total_power_wp = int(form.get("total_power_wp")) if form.get("total_power_wp") else None
    solar.expected_annual_yield_kwh = (
        int(form.get("expected_annual_yield_kwh")) if form.get("expected_annual_yield_kwh") else None
    )

    db.commit()
    return RedirectResponse("/assets?message=Zonnepanelen+opgeslagen", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/assets/battery", include_in_schema=False)
async def assets_battery_save(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    form = await request.form()
    battery = db.query(Battery).filter(Battery.owner_id == user.id).first()
    if not battery:
        battery = Battery(owner_id=user.id)
        db.add(battery)

    battery.purchase_date = _safe_date(form.get("purchase_date"))
    battery.purchase_cost_eur = _safe_float(form.get("purchase_cost_eur"))
    battery.capacity_kwh = _safe_float(form.get("capacity_kwh"))
    battery.brand_model = form.get("brand_model") or None

    db.commit()
    return RedirectResponse("/assets?message=Batterij+opgeslagen", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/cars", include_in_schema=False)
async def cars_view(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    cars = db.query(Car).filter(Car.owner_id == user.id).order_by(Car.name.asc()).all()
    return templates.TemplateResponse(
        "cars.html",
        {
            "request": request,
            "user": user,
            "cars": cars,
            "message": request.query_params.get("message"),
        },
    )


@app.post("/cars", include_in_schema=False)
async def cars_create(
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    form = await request.form()
    name = form.get("name")
    if not name:
        return RedirectResponse("/cars?message=Naam+is+verplicht", status_code=status.HTTP_303_SEE_OTHER)

    car = Car(
        owner_id=user.id,
        name=name,
        reimbursement_rate_ex_vat_eur_kwh=_safe_float(form.get("rate_ex_vat")),
        reimbursement_rate_inc_vat_eur_kwh=_safe_float(form.get("rate_inc_vat")),
        is_active=True,
    )
    db.add(car)
    db.commit()
    return RedirectResponse("/cars?message=Auto+toegevoegd", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/cars/{car_id}", include_in_schema=False)
async def cars_update(
    car_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    form = await request.form()
    car = db.query(Car).filter(Car.id == car_id, Car.owner_id == user.id).first()
    if not car:
        return RedirectResponse("/cars?message=Auto+niet+gevonden", status_code=status.HTTP_303_SEE_OTHER)

    car.name = form.get("name") or car.name
    car.reimbursement_rate_ex_vat_eur_kwh = _safe_float(form.get("rate_ex_vat"))
    car.reimbursement_rate_inc_vat_eur_kwh = _safe_float(form.get("rate_inc_vat"))
    car.is_active = form.get("is_active") == "on"

    db.commit()
    return RedirectResponse("/cars?message=Auto+bijgewerkt", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/cars/{car_id}/delete", include_in_schema=False)
async def cars_delete(
    car_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
):
    user = _require_user(request, db)
    car = db.query(Car).filter(Car.id == car_id, Car.owner_id == user.id).first()
    if car:
        db.delete(car)
        db.commit()
    return RedirectResponse("/cars?message=Auto+verwijderd", status_code=status.HTTP_303_SEE_OTHER)
