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


def get_items(path, api_key):
    now = timezone.now()
    time_limit = now - timedelta(days=1)
    any_items_exist = Item.objects.filter(part_path=path).exists()
    old_items = Item.objects.filter(part_path=path, updated_at__lte=time_limit).exists()

    if not any_items_exist or any_items_exist and old_items:
        url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        params = {
            'path': path,
            'public_key': api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get('_embedded', {}).get('items', [])
        return items
    else:
        items = []
        for item in Item.objects.filter(part_path=path).values('path', 'url', 'name', 'mime_type'):
            items.append({
                'path': item['path'],
                'file': item['url'],
                'name': item['name'],
                'mime_type': item['mime_type']
            })
        return items


def create_results(items):
    results = []
    for item in items:
        result_item = {
            'path': item.get('path'),
            'name': None,
            'url': None,
            'mime_type': item.get('mime_type'),
        }
        results.append(result_item)

    for result in results:
        for item in items:
            if result['path'] == item.get('path'):
                result['name'] = result['path'].rsplit('/', 1)[-1]
                result['part_path'] = result['path'].rsplit('/', 1)[0]
                result['url'] = item.get('file')
                Item.objects.update_or_create(
                    path=result['path'],
                    defaults={
                        'name': result['name'],
                        'part_path': result['part_path'],
                        'url': result['url'],
                        'mime_type': result['mime_type'],
                        'updated_at': timezone.now()
                    }
                )
    return results


def yandex_disk_request(request):
    api_key = request.session.get('api_key')
    path = request.session.get('path', '')

    if 'path' in request.GET:
        path = request.GET.get('path')
        request.session['path'] = path

    back = get_back(path)
    items = get_items(path, api_key)
    results = create_results(items)

    for result in results:
        result['path'] = f"/diskviewer/?path={result['path']}"

    return render(request, 'yandex_disk.html', {'items': results, 'path': path, 'back': back})
