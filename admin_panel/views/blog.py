from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView, UpdateView, View, CreateView
from django.contrib import messages
from user.mixins.logins import AdminUserMixin
from django.shortcuts import get_object_or_404, redirect, reverse, render
from blog.models import Blog, BlogCategory
from admin_panel.forms import AddBlogCategoryModelForm, AddBlogModelForm, AdminBlogFilteringForm


class BlogSetSortNumber(AdminUserMixin, RedirectView):
    """
    set sort number for blog
    """

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        sort_number = self.request.POST.get(f'{pk}')

        try:
            sort_number = int(sort_number)
            if 100000000 >= sort_number >= 0:
                post = get_object_or_404(Blog, pk=pk)
                post.sort_number = sort_number
                post.save()
                messages.success(self.request,'ثبت شد')
            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 تا  100,000,000 باشد'
                )

        except Exception as e:
            messages.error(
                self.request,
                'لطفا در وارد کردن عدد دقت فرمایید'
            )

        return reverse('admin_panel:blog-list')


class BlogListView(AdminUserMixin, ListView):
    """
    for listing the posts
    """

    model = Blog
    template_name = "admin_panel/blog/list.html"
    paginate_by = 100
    context_object_name = "items"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'views', 'store' , 'category'
        ).annotate(views_count=Count('views')).order_by('-id')
    
    def get_queryset(self):
        query = super().get_queryset().prefetch_related('views', 'store' , 'category'
        ).annotate(views_count=Count('views')).order_by('-id')

        form = AdminBlogFilteringForm(self.request.GET)

        if not form.is_valid():
            return query

        data = form.cleaned_data

        if store := data.get("store"):
            query = query.filter(store=store)
        if user_number := data.get("user_number"):
            query = query.filter(user__PhoneNumber=user_number)
        if start_date := data.get("start_date"):
            query = query.filter(updated_at__gte=start_date, is_active=True)
        if end_date := data.get("end_date"):
            query = query.filter(updated_at__lte=end_date, is_active=True)
        if category := data.get("category"):
            query = query.filter(category=category)
        if is_active := data.get("is_active"):
            if is_active == "11":
                query = query.filter(is_active=True)
            elif is_active == "12":
                query = query.filter(is_active=False)
        if is_active := data.get("admin_verified"):
            if is_active == "11":
                query = query.filter(admin_verified=True)
            elif is_active == "12":
                query = query.filter(admin_verified=False)

        if ordering := data.get("ordering"):
            if ordering == "11":  # جدید ترین
                query = query.order_by("-id")
            elif ordering == "12":  # قدیمی ترین
                query = query.order_by("id")
            elif ordering == "21":  # بیشترین بازدید
                query = query.annotate(view_count=Count("views")).order_by(
                    "-view_count"
                )
            elif ordering == "22":  # کمترین بازید
                query = query.annotate(view_count=Count("views")).order_by("view_count")        
            elif ordering == "23":  # کمترین بازید
                query = query.order_by("-sort_number")

        if title := data.get("title"):
            query = query.filter(
                Q(title__icontains=title) | Q(content__icontains=title)
            )

        return query
    

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["form"] = AdminBlogFilteringForm()
        return data
    

class BlogCreate(AdminUserMixin, CreateView):
    """for creating the post"""

    model = Blog
    template_name = "admin_panel/blog/create.html"
    form_class = AddBlogModelForm
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:blog-list")

    def dispatch(self, request, *args, **kwargs):
        messages.warning(
            self.request,
            "توجه داشته باشید اگر نوسینده انتخابی کارمند فروشگاه انتخابی نباشد تغییرات اعمال نخواهد شد باید از اول اقدام کنید",
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        store_users = form.cleaned_data.get('store').users

        if not store_users.filter(pk=form.cleaned_data.get('user').id).exists():
            messages.warning(
                self.request,
                'نویسنده انتخابی باید کارمند فروشگاه انتخابی باشد, کارمندان فروشگاه انتخابی شماره زیر می باشند :'
            )
            messages.info(
                self.request,
                ''.join(str(item.PhoneNumber).replace(' ', '') + ' | ' for item in store_users.all())
            )
            return redirect(self.request.META.get('HTTP_REFERER'))

        form.instance.admin_verified = False
        form.save()
        messages.success(self.request, "پست ساخته شد")
        return super().form_valid(form)


class BlogUpdate(AdminUserMixin, UpdateView):
    """for updating the post"""

    model = Blog
    template_name = "admin_panel/blog/create.html"
    form_class = AddBlogModelForm
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:blog-list")

    def dispatch(self, request, *args, **kwargs):
        messages.warning(
            self.request,
            "لطفا هنگام تغییرات این پست فروشگاه یا نویسنده مربوطه را مطلع فرمایید",
        )
        messages.warning(
            self.request,
            "توجه داشته باشید اگر نوسینده انتخابی کارمند فروشگاه انتخابی نباشد تغییرات اعمال نخواهد شد باید از اول اقدام کنید",
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        store_users = form.cleaned_data.get('store').users

        if not store_users.filter(pk=form.cleaned_data.get('user').id).exists():
            messages.warning(
                self.request,
                'نویسنده انتخابی باید کارمند فروشگاه انتخابی باشد, کارمندان فروشگاه انتخابی شماره زیر می باشند :'
            )
            messages.info(
                self.request,
                ''.join(str(item.PhoneNumber).replace(' ', '') + ' | ' for item in store_users.all())
            )
            return redirect(self.request.META.get('HTTP_REFERER'))

        form.save()
        messages.success(self.request, "تغییرات اعمال شد")
        return super().form_valid(form)


class BlogActiveAndDeactivate(AdminUserMixin, View):
    """for activating and deactivating posts"""

    def dispatch(self, request, *args, **kwargs):
        messages.warning(
            self.request,
            "لطفا هنگام تغییرات این پست فروشگاه یا نویسنده مربوطه را مطلع فرمایید",
        )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        obj = get_object_or_404(Blog, id=id)

        if obj.admin_verified:
            obj.admin_verified = False
            obj.save()
            messages.success(self.request, "پست شما با موفقیت غیر فعال شد")
        else:
            obj.admin_verified = True
            obj.save()
            messages.success(self.request, "پست شما با موفقیت  فعال شد")

        return redirect("admin_panel:blog-list")


class BlogDelete(AdminUserMixin, View):
    """for deleting posts"""

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(Blog, id=kwargs.get("pk"))
        messages.warning(
            self.request,
            "برای حذف  این پست لطفا فروشگاه یا نویسنده مربوطه را مطلع فرمایید",
        )
        messages.warning(self.request, "بهتر است به جای حذف پست را غیر فعال کنید")
        return render(request, "admin_panel/blog/delete.html", {"item": obj})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Blog, id=kwargs.get("pk"))
        conform = request.POST.get("conform")
        if conform == "delete":
            obj.delete()
            messages.warning(request, "پست مورد نظر حذف شد")
        else:
            messages.warning(request, "عبارت را درست وارد کنید")

        return redirect("admin_panel:blog-list")


# categories


class BlogCategoryListView(AdminUserMixin, ListView):
    """for listing the blog categories"""

    model = BlogCategory
    template_name = "admin_panel/blog/categories/list.html"
    paginate_by = 25
    context_object_name = "items"

    def get_queryset(self):
 
        query = super().get_queryset().prefetch_related("children","parent","blogs")
 
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        views = self.request.GET.get("views")
        posts = self.request.GET.get("posts")

 
        if search:
            query = query.filter(name__icontains=search)

 
        if status == "active":
            query = query.filter(is_active=True)
        elif status == "inactive":
            query = query.filter(is_active=False)


        if posts:

            query = query.annotate(posts_count=Count("blogs"))

            if posts == "most_posts":
                query = query.order_by("-posts_count")
            elif posts == "least_posts":
                query = query.order_by("posts_count")
            elif status == "sort_number_ac":
                query = query.order_by('-sort_number')
            elif status == "sort_number_disac":
                query = query.order_by('sort_number')
            elif posts.isdigit():
                query = query.filter(posts_count=int(posts))

        return query.distinct()



class BlogCategoryChangeSortNumber(AdminUserMixin, RedirectView):
    """for change sort number product categories"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        category = get_object_or_404(BlogCategory, pk=pk)
        sort_number = self.request.POST[f'{pk}']

        try:
            sort_number = int(sort_number)
            if 1000 >= sort_number  >= 0:
                category.sort_number = sort_number
                category.save()
                messages.success(
                    self.request,
                    'ثبت شد'
                )
                return reverse("admin_panel:blog-category-list")

            else:
                messages.error(
                    self.request,
                    'عدد وارد شده باید بین 0 الی 1000 باشد'
                )
        except Exception as e:
            messages.error(
                self.request,
                'عدد وارد شده باید بین 0 الی 1000 باشد'
            )

        return reverse("admin_panel:blog-category-list")


class BlogCategoryCreate(AdminUserMixin, CreateView):
    """for create blog category"""

    model = BlogCategory
    template_name = "admin_panel/blog/categories/create.html"
    form_class = AddBlogCategoryModelForm
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:blog-category-list")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "دسته ساخته شد")
        return super().form_valid(form)


class BlogCategoryUpdate(AdminUserMixin, UpdateView):
    """for update blog category"""

    model = BlogCategory
    template_name = "admin_panel/blog/categories/create.html"
    form_class = AddBlogCategoryModelForm
    context_object_name = "item"
    success_url = reverse_lazy("admin_panel:blog-category-list")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "تغییرات اعمال شد")
        return super().form_valid(form)


class BlogCategoryActiveAndDeactivate(AdminUserMixin, RedirectView):
    """for activating and deactivating posts"""

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        obj = get_object_or_404(BlogCategory, id=pk)

        if obj.is_active:
            obj.is_active = False
            obj.save()
            messages.success(self.request, "دسته مورد نظر غیر فعال شد")
        else:
            obj.is_active = True
            obj.save()
            messages.success(self.request, "دسته مورد نظر فعال شد")

        return reverse("admin_panel:blog-category-list")


class BlogCategoryDelete(AdminUserMixin, View):
    """for deleting posts"""

    def get(self, request, *args, **kwargs):
        messages.error(
            self.request, "با حذف دسته تمامی پست های زیر مجموعه ان به مشکل بر می خورند"
        )
        messages.warning(
            self.request, "بهتر است که به جای حذف این دسته را غیر فعال کنید"
        )
        return render(
            request,
            "admin_panel/blog/categories/delete.html",
            {"item": get_object_or_404(BlogCategory, id=kwargs.get("pk"))},
        )

    def post(self, request, *args, **kwargs):
        conform = request.POST.get("conform")
        obj = get_object_or_404(BlogCategory, id=kwargs.get("pk"))
        if conform == "delete":
            obj.delete()
        messages.warning(request, "حذف شد")
        return redirect("admin_panel:blog-category-list")
