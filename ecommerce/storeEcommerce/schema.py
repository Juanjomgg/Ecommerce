import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order, OrderItem

# Define the types of the models
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "email", "username", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "created_at", "updated_at")

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = ("id", "order", "product", "quantity")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "user", "products", "total_price", "status", "created_at")

class ResponseMessage(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    customer = graphene.Field(CustomerType)


# Define the queries
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    customer_by_email = graphene.Field(CustomerType, email=graphene.ID(required=True))
    product_by_id = graphene.Field(ProductType, id=graphene.ID(required=True))
    order_by_id = graphene.Field(OrderType, id=graphene.ID(required=True))

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()

    def resolve_customer_by_email(root, info, email):
        return Customer.objects.filter(email=email).first()

    def resolve_product_by_id(root, info, id):
        return Product.objects.get(pk=id)

    def resolve_order_by_id(root, info, id):
        return Order.objects.get(pk=id)

# Mutations

# Customer mutations
# Create
class CreateCustomer(graphene.Mutation):
    response = graphene.Field(ResponseMessage)
    customer = graphene.Field(CustomerType)
     
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String( required=True)
        phone = graphene.String()

    def mutate(self, info, username, email, phone):
        customer = Customer(username=username, email=email, phone=phone)
        customer.set_password("12345")
        customer.save()
        message = f"Customer with email {customer.email} created successfully"
        response = ResponseMessage(success=True, message=message, customer=customer)
        return CreateCustomer(response=response, customer=customer)
        

# Update
class UpdateCustomer(graphene.Mutation):
    response = graphene.Field(ResponseMessage)
    customer = graphene.Field(CustomerType)

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String()
        phone = graphene.String()

    def mutate(self, info, email=None, username=None, phone=None):

        customer = Customer.objects.filter(email=email).first()
        if not customer:
            message = f"Customer with email {email} not found"
            response = ResponseMessage(success=False, message=message, customer=customer)
            return UpdateCustomer(response=response, customer=customer)
        
        if email:
            customer.email = email
        if username:
            customer.username = username
        if phone:
            customer.phone = phone

        customer.save()
        message = f"Customer with email {customer.email} updated successfully"
        response = ResponseMessage(success=True, message=message, customer=customer)
        return UpdateCustomer(response=response, customer=customer)

# Delete
class DeleteCustomer(graphene.Mutation):
    response = graphene.Field(ResponseMessage)
    customer = graphene.Field(CustomerType)

    class Arguments:
        email = graphene.String(required=True)
        success = graphene.Boolean()

    def mutate(self, info, email):
        customer = Customer.objects.filter(email=email).first()
        if not customer:
            message = f"Customer with email {email} not found"
            response = ResponseMessage(success=False, message=message, customer=customer)
            return DeleteCustomer(response=response, customer=customer)
        
        customer.delete()
        message = f"Customer with email {email} deleted successfully"
        response = ResponseMessage(success=True, message=message, customer=customer)
        return DeleteCustomer(response=response, customer=customer)

# Product mutations
class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        price = graphene.String(required=True)
        stock = graphene.Int(required=True)

    def mutate(self, info, name, description=None, price=0.0, stock=0):
        product = Product(name=name, description=description, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

# Order mutations
class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        user_id = graphene.ID(required=True)
        products = graphene.List(graphene.ID, required=True)

    def mutate(self, info, user_id, products):
        user = Customer.objects.get(pk=user_id)
        products = Product.objects.filter(id__in=products)

        if not products:
            raise Exception("Products not found")
        
        total_price = sum(product.price for product in products)
        order = Order(user=user, total_price=total_price)
        order.save()

        for product in products:
            OrderItem.objects.create(order=order, product=product, quantity=1)
        
        return CreateOrder(order=order)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    update_customer = UpdateCustomer.Field()
    delete_customer = DeleteCustomer.Field()

    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)