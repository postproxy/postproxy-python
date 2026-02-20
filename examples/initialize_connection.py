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


if __name__ == "__main__":
    asyncio.run(main())
