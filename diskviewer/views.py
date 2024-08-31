from django.shortcuts import render, redirect
import requests
from datetime import timedelta
from django.utils import timezone
from .models import Item


def main(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        request.session['api_key'] = api_key
        request.session['path'] = ""
        return redirect('diskviewer')
    return render(request, 'main.html')


def get_back(path):
    last_slash_index = path.rfind('/')
    if last_slash_index != -1:
        path = path[:last_slash_index]
    else:
        path = "/"
    back = f"/diskviewer/?path={path}"
    return back


def get_items(part_path, api_key):
    now = timezone.now()
    time_limit = now - timedelta(days=1)
    any_items_exist = Item.objects.filter(part_path=part_path, api_key=api_key).exists()
    old_items = Item.objects.filter(part_path=part_path, api_key=api_key, updated_at__lte=time_limit).exists()

    if not any_items_exist or old_items:
        url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        params = {
            'path': part_path,
            'public_key': api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get('_embedded', {}).get('items', [])
        return items
    else:
        items = []
        for item in Item.objects.filter(part_path=part_path, api_key=api_key).values('name', 'url', 'mime_type'):
            items.append({
                'name': item['name'],
                'file': item['url'],
                'mime_type': item['mime_type']
            })
        return items


def create_results(items, part_path, api_key):
    results = []
    for item in items:
        result_item = {
            'name': item.get('name') or item['path'].rsplit('/', 1)[-1],
            'part_path': part_path,
            'url': item.get('file'),
            'mime_type': item.get('mime_type'),
        }
        results.append(result_item)

        Item.objects.update_or_create(
            name=result_item['name'],
            part_path=result_item['part_path'],
            api_key=api_key,
            defaults={
                'url': result_item['url'],
                'mime_type': result_item['mime_type'],
                'updated_at': timezone.now()
            }
        )

    return results


def yandex_disk_request(request):
    api_key = request.session.get('api_key')
    part_path = request.session.get('part_path', '')

    if 'path' in request.GET:
        part_path = request.GET.get('path')
        request.session['part_path'] = part_path

    back = get_back(part_path)
    items = get_items(part_path, api_key)
    results = create_results(items, part_path, api_key)  # Передаем part_path

    for result in results:
        result['path'] = f"/diskviewer/?path={result['part_path']}/{result['name']}"

    return render(request, 'yandex_disk.html', {'items': results, 'path': part_path, 'back': back})
