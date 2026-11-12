from pydantic import BaseModel, ConfigDict, Field, model_validator


class CurrentWeatherResponse(BaseModel):
    city: str
    temp: float
    feels_like: float
    condition: str
    description: str
    icon: str
    humidity: int
    wind_speed: float
    lat: float | None = None
    lon: float | None = None


class WeatherSlotResponse(BaseModel):
    temp: float
    feels_like: float
    condition: str
    description: str
    icon: str
    humidity: int
    wind_speed: float


class DaySlotsResponse(BaseModel):
    city: str
    slots: dict[str, WeatherSlotResponse]


class ActivityToEnrich(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    activity: str = Field(min_length=1, max_length=200)


class ActivityEnrichmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1, max_length=100)
    activities: list[ActivityToEnrich] = Field(max_length=8)


class EnrichedActivityResponse(BaseModel):
    time: str
    location: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=250)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def coordinates_must_be_a_pair(self):
        if (self.lat is None) != (self.lon is None):
            raise ValueError("lat and lon must both be set or both be null")
        return self


class ActivityEnrichmentResponse(BaseModel):
    activities: list[EnrichedActivityResponse]
