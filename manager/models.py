from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager


class Study(ExportModelOperationsMixin("study"), models.Model):
    class Status(models.IntegerChoices):
        RECRUITING = 1
        IN_PROGRESS = 2
        FINISHED = 3
        COMPLETED = 4

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="own_studies"
    )
    title = models.CharField(max_length=100)
    tags = TaggableManager()
    start = models.DateField()
    end = models.DateField()
    members = models.ManyToManyField(User, related_name="joined_studies")
    process = models.TextField()
    info = models.TextField()
    status = models.IntegerField(choices=Status.choices, default=Status.RECRUITING)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.creator}의 스터디 {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["creator"]),
        ]
        ordering = ["-created_at"]

    def finished_task(self):
        return self.study_tasks.filter(is_finished=True)

    def finished_task_percent(self):
        return round(
            float(
                len(self.study_tasks.filter(is_finished=True))
                / len(self.study_tasks.all())
            )
            * 100,
            2,
        )


class Task(ExportModelOperationsMixin("task"), models.Model):
    study = models.ForeignKey(
        Study, on_delete=models.CASCADE, related_name="study_tasks"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_tasks"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    start = models.DateField()
    end = models.DateField()
    is_finished = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.study}의 할 일 : {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["study"]),
        ]
        ordering = ["-created_at"]


class File(ExportModelOperationsMixin("file"), models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_file_name(self):
        return f"{self.name}.{self.url.split('.')[-1]}"

    def __str__(self):
        return self.get_file_name()


class Post(ExportModelOperationsMixin("post"), models.Model):
    title = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = MarkdownxField()
    files = models.ManyToManyField(File, related_name="posts", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task}에서 {self.author}의 게시글 : {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["title"]),
            models.Index(fields=["content"]),
        ]
        ordering = ["-created_at"]
