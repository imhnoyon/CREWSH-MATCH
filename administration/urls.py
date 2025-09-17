from django.urls import path

from .views import (
    Signin,
    ListUser,
    RetrieveUpdateDeleteUser,
    ListPrivateMode,
    ListSubscription,
    ListCreatePlan,
    DeletePlan,
    ListCreateCompany,
    RetrieveDeleteCompany,
    ListCreateShip,
    RetrieveUpdateDeleteShip,
    CreateAnnounceMent,
    UpdateAccount,
    SiteSettings,
    Dashboard
)


urlpatterns = [
    path("auth/sign-in/", Signin.as_view(), name='admin-signin'),
    path("user/list/", ListUser.as_view(), name='list-user'),
    path("user/retrieve-update-delete/<int:pk>/", RetrieveUpdateDeleteUser.as_view(), name='retrieve-update-delete'),
    path("subscription/private-mode/", ListPrivateMode.as_view(), name='list-private-mode'),
    path("subscription/list/", ListSubscription.as_view(), name='list-subscription'),
    path("plan/list-create/", ListCreatePlan.as_view(), name='list-create-plan'),
    path("plan/delete/<int:pk>/", DeletePlan.as_view(), name='delete-plan'),
    path("company/list-create/", ListCreateCompany.as_view(), name='list-create-company'),
    path("company/retrieve-update-delete/<int:pk>/", RetrieveDeleteCompany.as_view(), name='retrieve-update-delete-company'),
    path("ship/list-create/", ListCreateShip.as_view(), name='list-create-ship'),
    path("ship/retrieve-update-delete/<int:pk>/", RetrieveUpdateDeleteShip.as_view(), name='retrieve-update-delete-ship'),
    path("announcement/create/", CreateAnnounceMent.as_view(), name='create-announcement'),
    path("account/update/", UpdateAccount.as_view(), name='update-account'),
    path("site/settings/", SiteSettings.as_view(), name="site-settings"),
    path("dashboard/analytics/", Dashboard.as_view(), name='dashboard-analytics'),
]
