"""Example of managing a Google Business Profile location's own data."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_ID = "your-google-business-profile-id"


async def main():
    async with PostProxy(API_KEY) as client:
        gbp = client.google_business

        # location_id is the placement id of the location
        placements = (await client.profiles.placements(PROFILE_ID)).data
        location_id = placements[0].id

        # Read and update the location
        location = await gbp.location(
            PROFILE_ID, location_id, read_mask="title,phoneNumbers,websiteUri,regularHours"
        )
        print("Location:", location)

        await gbp.update_location(
            PROFILE_ID, location_id, ["websiteUri"], {"websiteUri": "https://example.com"}
        )

        # Opening hours: Mon-Fri 9-17
        weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        await gbp.update_hours(
            PROFILE_ID,
            location_id,
            fields=["regularHours"],
            regular_hours={
                "periods": [
                    {
                        "openDay": day,
                        "openTime": {"hours": 9},
                        "closeDay": day,
                        "closeTime": {"hours": 17},
                    }
                    for day in weekdays
                ]
            },
        )

        # Booking link
        types = await gbp.available_place_action_types(PROFILE_ID, location_id)
        print("Available action types:", types)
        await gbp.create_place_action_link(
            PROFILE_ID,
            location_id,
            uri="https://book.example.com",
            place_action_type="APPOINTMENT",
            is_preferred=True,
        )

        # Add a storefront photo
        await gbp.create_media(
            PROFILE_ID,
            location_id,
            "https://example.com/storefront.jpg",
            category="EXTERIOR",
            media_format="PHOTO",
        )
        print("Media:", await gbp.media(PROFILE_ID, location_id))


if __name__ == "__main__":
    asyncio.run(main())
