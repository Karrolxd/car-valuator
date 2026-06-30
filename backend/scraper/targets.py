from dataclasses import dataclass, field


@dataclass(frozen=True)
class Target:
    brand: str
    model: str
    brand_slug: str
    model_slug: str
    # slug używany w URL (może być inny niż model_slug)
    url_slug: str = ""
    # slugi które akceptujemy przy filtracji (startswith)
    # jeśli puste — używamy model_slug
    model_slug_variants: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        # jeśli url_slug nie podany — używamy model_slug
        if not self.url_slug:
            object.__setattr__(self, "url_slug", self.model_slug)

    def matches_model_slug(self, slug: str) -> bool:
        """Czy slug z ogłoszenia pasuje do tego targetu."""
        if not slug:
            return True
        variants = self.model_slug_variants if self.model_slug_variants else (self.model_slug,)
        return any(slug.startswith(v) for v in variants)


TARGETS: list[Target] = [
    # Volkswagen
    Target("Volkswagen", "Golf", "volkswagen", "golf"),
    Target("Volkswagen", "Passat", "volkswagen", "passat"),
    Target("Volkswagen", "Polo", "volkswagen", "polo"),
    Target("Volkswagen", "Tiguan", "volkswagen", "tiguan"),
    # Toyota
    Target("Toyota", "Corolla", "toyota", "corolla"),
    Target("Toyota", "Yaris", "toyota", "yaris"),
    Target("Toyota", "RAV4", "toyota", "rav4"),
    Target("Toyota", "Auris", "toyota", "auris"),
    # BMW
    Target("BMW", "Seria 3", "bmw", "seria-3"),
    Target("BMW", "Seria 5", "bmw", "seria-5"),
    Target("BMW", "X5", "bmw", "x5"),
    Target("BMW", "X3", "bmw", "x3"),
    # Mercedes-Benz
    Target("Mercedes-Benz", "Klasa C", "mercedes-benz", "klasa-c"),
    Target("Mercedes-Benz", "Klasa E", "mercedes-benz", "klasa-e"),
    Target("Mercedes-Benz", "GLC", "mercedes-benz", "glc"),
    # Audi A4 — dwa osobne URL-e, jeden model w bazie
    Target(
        "Audi", "A4", "audi", "a4",
        url_slug="a4-limousine",
        model_slug_variants=("a4-limousine",),
    ),
    Target(
        "Audi", "A4", "audi", "a4",
        url_slug="a4-avant",
        model_slug_variants=("a4-avant",),
    ),
    # Audi A3
    Target(
        "Audi", "A3", "audi", "a3",
        url_slug="a3-sportback",
        model_slug_variants=("a3-sportback", "a3-limousine", "a3-3-drzwiowe"),
    ),
    # Audi A6
    Target(
        "Audi", "A6", "audi", "a6",
        url_slug="a6-limousine",
        model_slug_variants=("a6-limousine",),
    ),
    Target(
        "Audi", "A6", "audi", "a6",
        url_slug="a6-avant",
        model_slug_variants=("a6-avant", "a6-allroad"),
    ),
    Target("Audi", "Q5", "audi", "q5"),
    # Skoda
    Target("Skoda", "Octavia", "skoda", "octavia"),
    Target("Skoda", "Fabia", "skoda", "fabia"),
    Target("Skoda", "Superb", "skoda", "superb"),
    Target("Skoda", "Karoq", "skoda", "karoq"),
    # Ford
    Target("Ford", "Focus", "ford", "focus"),
    Target("Ford", "Mondeo", "ford", "mondeo"),
    Target("Ford", "Kuga", "ford", "kuga"),
    # Opel
    Target("Opel", "Astra", "opel", "astra"),
    Target("Opel", "Insignia", "opel", "insignia"),
    Target("Opel", "Corsa", "opel", "corsa"),
    # Hyundai
    Target("Hyundai", "i30", "hyundai", "i30"),
    Target("Hyundai", "Tucson", "hyundai", "tucson"),
    # Kia
    Target("Kia", "Ceed", "kia", "ceed"),
    Target("Kia", "Sportage", "kia", "sportage"),
    # Renault
    Target("Renault", "Megane", "renault", "megane"),
    Target("Renault", "Clio", "renault", "clio"),
    # Peugeot
    Target("Peugeot", "308", "peugeot", "308"),
    Target("Peugeot", "508", "peugeot", "508"),
    # Mazda 6 i 3 — prawdziwe slugi to "6" i "3"
    Target(
        "Mazda", "Mazda 6", "mazda", "mazda-6",
        url_slug="6",
        model_slug_variants=("6",),
    ),
    Target(
        "Mazda", "Mazda 3", "mazda", "mazda-3",
        url_slug="3",
        model_slug_variants=("3",),
    ),
    Target("Mazda", "CX-5", "mazda", "cx-5"),
    # Honda
    Target("Honda", "Civic", "honda", "civic"),
    Target("Honda", "CR-V", "honda", "cr-v"),
    # Nissan
    Target("Nissan", "Qashqai", "nissan", "qashqai"),
    Target("Nissan", "X-Trail", "nissan", "x-trail"),
]


BASE_URL = "https://www.otomoto.pl/osobowe"


def build_search_url(target: Target, page: int = 1) -> str:
    url = f"{BASE_URL}/{target.brand_slug}/{target.url_slug}"
    if page > 1:
        url += f"?page={page}"
    return url