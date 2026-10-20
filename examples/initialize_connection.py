"""Example of initializing a social platform connection."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID")


async def main():
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        # List profile groups
        groups = (await client.profile_groups.list()).data
        print("Profile groups:")
        for g in groups:
            print(f"  {g.id}: {g.name} ({g.profiles_count} profiles)")

        # Use the first group (or create one)
        if groups:
            group = groups[0]
        else:
            group = await client.profile_groups.create("My Group")
            print(f"\nCreated group: {group.id}")

        # Initialize a connection for a platform
        conn = await client.profile_groups.initialize_connection(
            group.id,
            platform="instagram",
            redirect_url="https://yourapp.com/callback",
        )
        print(f"\nRedirect the user to: {conn.url}")

        # Instagram via Facebook login (needed to attach music to reels)
        ig_via_facebook = await client.profile_groups.initialize_connection(
            group.id,
            platform="instagram",
            redirect_url="https://yourapp.com/callback",
            onboarding="facebook",
        )
        print(f"Instagram (Facebook login) URL: {ig_via_facebook.url}")

        # WhatsApp through the WhatsApp Business app ("api" for the Cloud API)
        whatsapp = await client.profile_groups.initialize_connection(
            group.id,
            platform="whatsapp",
            redirect_url="https://yourapp.com/callback",
            onboarding="business_app",
        )
        print(f"WhatsApp URL: {whatsapp.url}")

        # After connecting, list a profile's placements (Pages, channels, locations)
        placements = (await client.profiles.placements("profile-id")).data
        print("Placements:", [(p.id, p.name) for p in placements])

        # Move one placement to a different profile group
        if placements:
            await client.profiles.assign_placement_to_group(
                "profile-id",
                placement_id=placements[0].id,
                target_profile_group_id="other-group-id",
            )


if __name__ == "__main__":
    asyncio.run(main())
