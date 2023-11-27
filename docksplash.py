#!/usr/bin/python3

import click
import requests

def list_repositories(registry_url):
    response = requests.get(f"{registry_url}/v2/_catalog")
    response.raise_for_status()
    repositories = response.json()["repositories"]
    return repositories

def list_tags(registry_url, repository):
    response = requests.get(f"{registry_url}/v2/{repository}/tags/list")
    response.raise_for_status()
    tags = response.json()["tags"]
    return tags

def get_image_sha(registry_url, repository, tag):
    response = requests.get(f"{registry_url}/v2/{repository}/manifests/{tag}", headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"})
    response.raise_for_status()
    sha = response.headers["Docker-Content-Digest"]
    return sha

@click.command()
@click.argument("registry_url")
def docksplash(registry_url):
    repositories = list_repositories(registry_url)
    selected_repo = 0

    while True:
        click.clear()
        click.echo("Docker Registry Explorer\n")

        for i, repo in enumerate(repositories):
            if i == selected_repo:
                click.echo(f"-> {repo} <-")
            else:
                click.echo(f"   {repo}")

        click.echo("\nUse arrow keys (j/k) to navigate, (l/enter) to select, (h/q) to go back.")

        key = click.getchar()

        if key in ("q", "h"):
            break
        elif key in ("j", "\x1b[B"):  # down arrow
            selected_repo = (selected_repo + 1) % len(repositories)
        elif key in ("k", "\x1b[A"):  # up arrow
            selected_repo = (selected_repo - 1) % len(repositories)
        elif key in ("l", "\r"):  # enter or 'l'
            selected_tags = list_tags(registry_url, repositories[selected_repo])
            selected_tag = 0

            while True:
                click.clear()
                click.echo(f"Tags for {repositories[selected_repo]}\n")

                for i, tag in enumerate(selected_tags):
                    if i == selected_tag:
                        click.echo(f"-> {tag} <-")
                    else:
                        click.echo(f"   {tag}")

                click.echo("\nUse arrow keys (j/k) to navigate, (l/enter) to select, (h/q) to go back.")

                key = click.getchar()

                if key in ("q", "h"):
                    break
                elif key in ("j", "\x1b[B"):  # down arrow
                    selected_tag = (selected_tag + 1) % len(selected_tags)
                elif key in ("k", "\x1b[A"):  # up arrow
                    selected_tag = (selected_tag - 1) % len(selected_tags)
                elif key in ("l", "\r"):  # enter or 'l'
                    selected_sha = get_image_sha(registry_url, repositories[selected_repo], selected_tags[selected_tag])
                    click.echo(f"\nSHA256 for {repositories[selected_repo]}:{selected_tags[selected_tag]}: {selected_sha}")
                    click.echo("\nPress (h/q) to go back.")
                    key = click.getchar()
                    if key in ("q", "h"):
                        break

if __name__ == "__main__":
    docksplash()
