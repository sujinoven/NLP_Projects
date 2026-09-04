from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    main_category: str
    sub_category: str
    image: str | None = None
    link: str | None = None
    ratings: float | None = None
    no_of_ratings: float | None = None
    discount_price: float | None = None
    actual_price: float | None = None
    similarity_score: float | None = None


class RecommendationResponse(BaseModel):
    selected_product: Product
    recommendations: list[Product]
    message: str = ""
