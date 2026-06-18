from abc import ABC, abstractmethod


class BaseProduct(ABC):
    warehouse_name = "Amazon Logistics"
    base_storage_fee = 5000

    def __init__(self, product_code, product_name):
        self.product_code = product_code
        self.product_name = product_name
        self.__stock_quantity = 0

    @property
    def stock_quantity(self):
        return self.__stock_quantity

    def _set_stock_quantity(self, value):
        self.__stock_quantity = value

    @property
    def product_name(self):
        return self._product_name

    @product_name.setter
    def product_name(self, value):
        self._product_name = value.strip().upper()

    @staticmethod
    def validate_product_code(product_code):
        return (
            len(product_code) == 10
            and product_code[0].isalpha()
            and product_code.isalnum()
        )

    @classmethod
    def update_warehouse_name(cls, new_name):
        cls.warehouse_name = new_name

    @abstractmethod
    def import_stock(self, quantity):
        pass

    @abstractmethod
    def export_stock(self, quantity):
        pass

    def __add__(self, other):
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity + other.stock_quantity

    def __lt__(self, other):
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity < other.stock_quantity


class ColdStorageProduct(BaseProduct):
    def __init__(self, product_code, product_name, required_temperature):
        super().__init__(product_code, product_name)
        self.required_temperature = required_temperature

    def import_stock(self, quantity):
        self._set_stock_quantity(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        loss = quantity * 0.05
        total = quantity + loss

        if total > self.stock_quantity:
            print("Không đủ tồn kho.")
            return

        self._set_stock_quantity(self.stock_quantity - total)

        print("Xuất kho thành công!")
        print(f"Số lượng yêu cầu: {quantity}")
        print(f"Hao hụt: {loss}")
        print(f"Tổng khấu trừ: {total}")

    def apply_cooling_cost(self):
        return self.stock_quantity * abs(self.required_temperature) * 30


class HazardousProduct(BaseProduct):
    def __init__(self, product_code, product_name, max_safety_limit):
        super().__init__(product_code, product_name)
        self.max_safety_limit = max_safety_limit

    def import_stock(self, quantity):
        if self.stock_quantity + quantity > self.max_safety_limit:
            print("Vượt quá hạn mức an toàn.")
            return
        self._set_stock_quantity(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        if quantity > self.stock_quantity:
            print("Không đủ tồn kho.")
            return
        self._set_stock_quantity(self.stock_quantity - quantity)


class HybridPremiumProduct(ColdStorageProduct, HazardousProduct):
    def __init__(
        self,
        product_code,
        product_name,
        required_temperature,
        max_safety_limit,
    ):
        BaseProduct.__init__(self, product_code, product_name)
        self.required_temperature = required_temperature
        self.max_safety_limit = max_safety_limit

    def import_stock(self, quantity):
        if self.stock_quantity + quantity > self.max_safety_limit:
            print("Vượt quá hạn mức an toàn.")
            return
        self._set_stock_quantity(self.stock_quantity + quantity)


class FedExCarrier:
    def ship_package(self, product, quantity):
        print(f"[FedEx] Tiếp nhận {product.product_code} - {quantity} đơn vị")


class DHLCarrier:
    def ship_package(self, product, quantity):
        print(f"[DHL] Tiếp nhận {product.product_code} - {quantity} đơn vị")


def dispatch_to_carrier(carrier_agent, product, quantity):
    try:
        carrier_agent.ship_package(product, quantity)
        product.export_stock(quantity)
    except AttributeError:
        print("Đơn vị vận chuyển không hợp lệ hoặc chưa ký kết hợp đồng kỹ thuật")


def show_product_info(product):
    print("\\n--- THÔNG TIN SẢN PHẨM ---")
    print("Loại:", type(product).__name__)
    print("Kho:", product.warehouse_name)
    print("Mã:", product.product_code)
    print("Tên:", product.product_name)
    print("Tồn kho:", product.stock_quantity)

    if isinstance(product, ColdStorageProduct):
        print("Nhiệt độ:", product.required_temperature)

    if isinstance(product, HazardousProduct) or isinstance(
        product, HybridPremiumProduct
    ):
        print("Hạn mức:", product.max_safety_limit)

    print("\\nMRO:")
    for cls in type(product).mro():
        print(cls.__name__)


def main():
    products = []
    current_product = None

    while True:
        print("\\n===== AMAZON INVENTORY SIMULATOR PRO =====")
        print("1. Đăng ký sản phẩm")
        print("2. Xem thông tin & MRO")
        print("3. Nhập / Xuất kho")
        print("4. Tính phí làm lạnh")
        print("5. Overloading")
        print("6. Duck Typing")
        print("7. Thoát")

        choice = input("Chọn: ")

        if choice == "1":
            try:
                print("1. Cold")
                print("2. Hazardous")
                print("3. Hybrid")

                t = input("Loại: ")
                code = input("Mã SP: ")

                if not BaseProduct.validate_product_code(code):
                    print("Mã sản phẩm không hợp lệ!")
                    continue

                name = input("Tên SP: ")

                if t == "1":
                    temp = float(input("Nhiệt độ: "))
                    current_product = ColdStorageProduct(code, name, temp)

                elif t == "2":
                    limit = int(input("Hạn mức: "))
                    current_product = HazardousProduct(code, name, limit)

                elif t == "3":
                    temp = float(input("Nhiệt độ: "))
                    limit = int(input("Hạn mức: "))
                    current_product = HybridPremiumProduct(code, name, temp, limit)

                products.append(current_product)
                print("Đăng ký thành công")

            except Exception as e:
                print("Lỗi:", e)

        elif choice == "2":
            if current_product:
                show_product_info(current_product)
            else:
                print("Chưa có sản phẩm.")

        elif choice == "3":
            if not current_product:
                print("Chưa có sản phẩm.")
                continue

            action = input("1.Nhập 2.Xuất: ")
            qty = float(input("Số lượng: "))

            if action == "1":
                current_product.import_stock(qty)
            else:
                current_product.export_stock(qty)

        elif choice == "4":
            if isinstance(
                current_product,
                (ColdStorageProduct, HybridPremiumProduct),
            ):
                cost = current_product.apply_cooling_cost()
                print("Chi phí:", f"{cost:,.0f} VND")
            else:
                print("Không hỗ trợ.")

        elif choice == "5":
            if len(products) < 2:
                print("Cần ít nhất 2 sản phẩm.")
                continue

            for i, p in enumerate(products):
                print(i, p.product_name)

            idx = int(input("Chọn sản phẩm đối ứng: "))

            other = products[idx]

            try:
                print("A < B =", current_product < other)
                print("A + B =", current_product + other)
            except TypeError:
                print("Lỗi overloading")

        elif choice == "6":
            if not current_product:
                print("Chưa có sản phẩm.")
                continue

            print("1. FedEx")
            print("2. DHL")

            c = input("Chọn: ")
            qty = float(input("Số lượng: "))

            carrier = FedExCarrier() if c == "1" else DHLCarrier()

            dispatch_to_carrier(carrier, current_product, qty)

        elif choice == "7":
            print("Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
